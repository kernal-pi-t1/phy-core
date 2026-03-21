"""
전자제품 반품 물류 스테이션 VLM 판정 노드 (ROS2 Service Server)

Input (VlmJudge.srv):
    - 물체의 다각도 이미지 경로 (앞/옆/뒤 등 2~4장)
    - 반품 물체 이름
    - 반품 사유 텍스트

Output:
    - RETURN_APPROVED  : 파손 없음 → 반품 가능
    - RETURN_REJECTED  : 파손 있음 → 반품 안됨
    - MANUAL_REVIEW    : 판단 애매 → 수동 검토
"""

import re
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from threading import Thread
from time import perf_counter, sleep

from packaging.version import Version


def require_package(package_name: str, minimum_version: str) -> None:
    try:
        installed_version = version(package_name)
    except PackageNotFoundError as exc:
        raise SystemExit(
            f"{package_name}>={minimum_version} is required but is not installed.\n"
            f"Install it with: python3 -m pip install '{package_name}>={minimum_version}'"
        ) from exc

    if Version(installed_version) < Version(minimum_version):
        raise SystemExit(
            f"{package_name}>={minimum_version} is required, but {installed_version} is installed.\n"
            f"Upgrade it with: python3 -m pip install --upgrade '{package_name}>={minimum_version}'"
        )


require_package("jinja2", "3.1.0")

import rclpy
import torch
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from tqdm import tqdm
from transformers import AutoModelForImageTextToText, AutoProcessor, BitsAndBytesConfig

from phy_interface.srv import VlmJudge


# =============================================================================
#  시스템 프롬프트
# =============================================================================
SYSTEM_PROMPT = """당신은 반품 물류 스테이션의 품질 검수 AI입니다.
고객이 반품 요청한 제품의 다각도 사진과 반품 사유를 보고 결함 여부를 판단하세요.

## 규칙
- 외관 결함(깨짐, 찌그러짐, 균열, 변형, 긁힘, 부품 누락 등)이 하나라도 보이면 → 결함 있음
- 포장이 개봉·뜯김·찢김·절개된 흔적이 있는 제품(과자 박스, 빼빼로 박스 등 밀봉 포장 제품)은 → 결함 있음
- 내용물이 있어야 하는 제품(음료수, 캔음료, 페트병 음료 등)의 경우, 내용물이 비어 있거나 현저히 부족하면 → 결함 있음
- 모든 각도에서 외관 결함이 전혀 없고, 포장도 미개봉 상태이며, 내용물이 있어야 하는 제품이라면 내용물도 정상적으로 채워져 있으면 → 결함 없음
- 결함 여부를 판단하기 어려우면 → 애매함

## 출력 형식 (반드시 이 형식을 따르세요)
결함 여부: [있음 / 없음 / 애매함]
근거: [2-3문장으로 작성. 결함이 확인된 경우 몇 번째 각도 사진에서 확인되었는지 명시. 예: "각도 2/3 사진에서 균열이 확인됨", "내용물이 비어 있음이 확인됨"]
"""


# =============================================================================
#  모델 로드
# =============================================================================
def load_model():
    processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct")
    model = AutoModelForImageTextToText.from_pretrained(
        "Qwen/Qwen2.5-VL-7B-Instruct",
        quantization_config=BitsAndBytesConfig(load_in_4bit=True),
        device_map="auto",
    )
    return processor, model


def generate_with_timing(model, **generate_kwargs):
    result: dict[str, object] = {}

    def run_generate() -> None:
        result["outputs"] = model.generate(**generate_kwargs)

    start_time = perf_counter()
    worker = Thread(target=run_generate, daemon=True)
    worker.start()

    with tqdm(desc="Inference", unit="s", bar_format="{desc}: {elapsed} elapsed") as progress:
        while worker.is_alive():
            sleep(0.1)
            progress.update(0)
        worker.join()
        elapsed = perf_counter() - start_time
        progress.set_postfix_str(f"{elapsed:.2f}s")

    return result["outputs"], perf_counter() - start_time


# =============================================================================
#  VLM 응답 파싱 & 판정
# =============================================================================
@dataclass
class ReturnJudgment:
    damage_status: str          # 있음 / 없음 / 애매함
    decision: str               # RETURN_APPROVED / RETURN_REJECTED / MANUAL_REVIEW
    reason: str                 # VLM이 작성한 근거
    vlm_raw: str                # VLM 원본 응답
    inference_time: float


def parse_response(vlm_response: str) -> tuple[str, str]:
    """VLM 응답에서 파손 여부와 근거를 파싱한다."""
    damage_match = re.search(r"결함\s*여부\s*[:：]\s*(있음|없음|애매함)", vlm_response)
    reason_match = re.search(r"근거\s*[:：]\s*(.+)", vlm_response, re.DOTALL)

    status = damage_match.group(1) if damage_match else "애매함"  # 파싱 실패 시 애매함으로 간주
    reason = reason_match.group(1).strip() if reason_match else vlm_response

    return status, reason


def apply_decision_rule(damage_status: str) -> str:
    """파손 여부 → 판정"""
    if damage_status == "없음":
        return "RETURN_APPROVED"
    if damage_status == "있음":
        return "RETURN_REJECTED"
    return "MANUAL_REVIEW"


# =============================================================================
#  반품 판정
# =============================================================================
def judge_return(
    processor,
    model,
    image_paths: list[Path],
    object_name: str,
    return_reason: str,
    max_new_tokens: int = 256,
) -> ReturnJudgment:
    """
    다각도 이미지와 반품 사유를 받아 VLM 판정을 수행한다.
    파손 있음 → RETURN_REJECTED, 파손 없음 → RETURN_APPROVED
    """
    # 이미지 콘텐츠 구성
    content = []
    for i, img_path in enumerate(image_paths, 1):
        if not img_path.exists():
            raise FileNotFoundError(f"이미지를 찾을 수 없음: {img_path}")
        content.append({"type": "image", "url": str(img_path)})
        content.append({"type": "text", "text": f"[각도 {i}/{len(image_paths)}]"})

    # 반품 정보 & 질의
    user_query = (
        f"\n## 반품 정보\n"
        f"- 제품명: {object_name}\n"
        f"- 반품 사유: {return_reason}\n\n"
        f"위 사진 {len(image_paths)}장은 **동일한 제품 1개**를 여러 각도에서 촬영한 것입니다.\n"
        f"제품에 파손이 있는지 판단하세요."
    )
    content.append({"type": "text", "text": user_query})

    messages = [
        {"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT}]},
        {"role": "user", "content": content},
    ]

    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)

    outputs, elapsed_time = generate_with_timing(model, **inputs, max_new_tokens=max_new_tokens)
    vlm_response = processor.decode(outputs[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)

    # 파싱 & 판정
    status, reason = parse_response(vlm_response)
    decision = apply_decision_rule(status)

    return ReturnJudgment(
        damage_status=status,
        decision=decision,
        reason=reason,
        vlm_raw=vlm_response,
        inference_time=elapsed_time,
    )


# =============================================================================
#  ROS2 Service Server Node
# =============================================================================
class VlmNode(Node):
    """VLM 판정 서비스 서버 노드.

    startup 시 모델을 1회 로드하고, vlm_judge 서비스 요청마다
    judge_return()을 호출하여 결과를 반환한다.
    """

    def __init__(self):
        super().__init__('vlm_node')

        self.get_logger().info('VLM 모델 로딩 중...')
        self._processor, self._model = load_model()
        self.get_logger().info('VLM 모델 로딩 완료')

        # 추론이 오래 걸리므로 MutuallyExclusive로 1건씩 처리
        self._srv_cb_group = MutuallyExclusiveCallbackGroup()
        self._service = self.create_service(
            VlmJudge, 'vlm_judge',
            self._judge_callback,
            callback_group=self._srv_cb_group,
        )
        self.get_logger().info('vlm_node ready. Service: vlm_judge')

    def _judge_callback(self, request, response):
        image_paths = [Path(p) for p in request.image_paths]
        self.get_logger().info(
            f'판정 요청: object="{request.object_name}", '
            f'reason="{request.return_reason}", images={len(image_paths)}장'
        )

        try:
            result = judge_return(
                processor=self._processor,
                model=self._model,
                image_paths=image_paths,
                object_name=request.object_name,
                return_reason=request.return_reason,
            )
            response.success = True
            response.decision = result.decision
            response.damage_status = result.damage_status
            response.reason = result.reason
            response.inference_time = result.inference_time

            self.get_logger().info(
                f'판정 결과: {result.decision} '
                f'(파손: {result.damage_status}, {result.inference_time:.2f}s)'
            )
        except Exception as e:
            self.get_logger().error(f'판정 실패: {e}')
            response.success = False
            response.decision = ''
            response.damage_status = ''
            response.reason = str(e)
            response.inference_time = 0.0

        return response


def main(args=None):
    rclpy.init(args=args)
    node = VlmNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
