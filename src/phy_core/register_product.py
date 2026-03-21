#!/usr/bin/env python3
"""Register product images for SAM3 detection.

Usage:
    python register_product.py --image /path/to/product.png --name "콜라"
    python register_product.py --image /path/to/product.png --name "콜라" --prompt "cola bottle"
    python register_product.py --list
    python register_product.py --delete "콜라"
"""

import argparse
import json
import os
import re
import shutil
from datetime import datetime

IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image")
PRODUCTS_JSON = os.path.join(IMAGE_DIR, "products.json")


def _load_products():
    if not os.path.exists(PRODUCTS_JSON):
        return {"products": []}
    with open(PRODUCTS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_products(data):
    with open(PRODUCTS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _sanitize_filename(name):
    """Convert product name to a safe filename (lowercase, underscores)."""
    name = name.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s-]+", "_", name)
    return name


def register(image_path, name, prompt=None):
    if not os.path.isfile(image_path):
        print(f"Error: '{image_path}' not found.")
        return False

    if not image_path.lower().endswith(".png"):
        print("Error: Only PNG files are supported.")
        return False

    os.makedirs(IMAGE_DIR, exist_ok=True)

    data = _load_products()

    # Check duplicate
    for p in data["products"]:
        if p["name"] == name:
            print(f"Error: '{name}' is already registered. Delete first to re-register.")
            return False

    filename = _sanitize_filename(name) + ".png"
    dest = os.path.join(IMAGE_DIR, filename)

    shutil.copy2(image_path, dest)

    sam3_prompt = prompt if prompt else name

    entry = {
        "name": name,
        "image": filename,
        "prompt": sam3_prompt,
        "registered_at": datetime.now().isoformat(timespec="seconds"),
    }
    data["products"].append(entry)
    _save_products(data)

    print(f"Registered: '{name}'")
    print(f"  Image  : {dest}")
    print(f"  Prompt : {sam3_prompt}")
    return True


def list_products():
    data = _load_products()
    if not data["products"]:
        print("No products registered.")
        return

    print(f"{'Name':<20} {'Prompt':<25} {'Image':<25} {'Registered'}")
    print("-" * 90)
    for p in data["products"]:
        print(f"{p['name']:<20} {p['prompt']:<25} {p['image']:<25} {p.get('registered_at', 'N/A')}")


def delete_product(name):
    data = _load_products()
    found = None
    for i, p in enumerate(data["products"]):
        if p["name"] == name:
            found = i
            break

    if found is None:
        print(f"Error: '{name}' not found.")
        return False

    entry = data["products"].pop(found)
    image_path = os.path.join(IMAGE_DIR, entry["image"])
    if os.path.exists(image_path):
        os.remove(image_path)
        print(f"Deleted image: {image_path}")

    _save_products(data)
    print(f"Deleted product: '{name}'")
    return True


def main():
    parser = argparse.ArgumentParser(description="Register product images for SAM3 detection")
    parser.add_argument("--image", type=str, help="Path to product PNG image")
    parser.add_argument("--name", type=str, help="Product name (used as identifier)")
    parser.add_argument("--prompt", type=str, help="SAM3 text prompt (defaults to --name)")
    parser.add_argument("--list", action="store_true", help="List registered products")
    parser.add_argument("--delete", type=str, metavar="NAME", help="Delete a registered product")

    args = parser.parse_args()

    if args.list:
        list_products()
    elif args.delete:
        delete_product(args.delete)
    elif args.image and args.name:
        register(args.image, args.name, args.prompt)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
