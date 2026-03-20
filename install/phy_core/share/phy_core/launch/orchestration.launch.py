"""Launch file for pick-and-place orchestration system.

Launches:
    - sam3_node: SAM3 perception service server
    - orchestration_node: State machine orchestrator

PYTHONPATH is extended to include:
    - /home/robot/jm_ws (for pose_estimator, capture_realsense)
    - /home/robot/jm_ws/sam3 (for sam3 package, needed by pose_estimator.py:194)
"""

import os

from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable
from launch_ros.actions import Node


def generate_launch_description():
    # Extend PYTHONPATH for pose_estimator and sam3 imports
    workspace_root = '/home/robot/jm_ws'
    extra_paths = os.pathsep.join([
        workspace_root,
        os.path.join(workspace_root, 'sam3'),
    ])
    existing_pythonpath = os.environ.get('PYTHONPATH', '')
    new_pythonpath = extra_paths + os.pathsep + existing_pythonpath

    config_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', 'config', 'waypoints.yaml'
    )

    return LaunchDescription([
        # Set PYTHONPATH before launching nodes
        SetEnvironmentVariable('PYTHONPATH', new_pythonpath),

        # SAM3 perception node (launch first, orchestrator waits for its services)
        Node(
            package='phy_core',
            executable='sam3_node',
            name='sam3_node',
            output='screen',
            parameters=[config_file],
        ),

        # Orchestration state machine node
        Node(
            package='phy_core',
            executable='orchestration_node',
            name='orchestration_node',
            output='screen',
            parameters=[config_file],
        ),
    ])
