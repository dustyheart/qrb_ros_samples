# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-License-Identifier: BSD-3-Clause-Clear

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    apriltag_conf = LaunchConfiguration("apriltag_conf")
    apriltag_conf_arg = DeclareLaunchArgument(
        "apriltag_conf",
        default_value=os.path.join(
            get_package_share_directory("sample_apriltag"),
            "config",
            "tags_41h12.yaml",
        ),
    )

    # rectify: subscribes to Orbbec's rgb8 + camera_info, publishes /apriltag/image_rect
    rectify = ComposableNode(
        name="rectify",
        package="image_proc",
        plugin="image_proc::RectifyNode",
        extra_arguments=[{"use_intra_process_comms": True}],
        remappings=[
            ("image", "/camera/color/image_raw"),
            ("camera_info", "/camera/color/camera_info"),
            ("image_rect", "/apriltag/image_rect"),
        ],
    )

    # apriltag_ros/AprilTagNode: subscribes to image_rect + camera_info, publishes /apriltag/detections + /tf
    apriltag = ComposableNode(
        name="apriltag",
        package="apriltag_ros",
        plugin="AprilTagNode",
        namespace="apriltag",
        parameters=[apriltag_conf],
        extra_arguments=[{"use_intra_process_comms": True}],
        remappings=[
            ("image_rect", "/apriltag/image_rect"),
            ("camera_info", "/camera/color/camera_info"),
        ],
    )

    container = ComposableNodeContainer(
        name="apriltag_container",
        namespace="",
        package="rclcpp_components",
        executable="component_container",
        composable_node_descriptions=[rectify, apriltag],
        output="screen",
    )

    orbbec_launch = os.path.join(
        get_package_share_directory("orbbec_camera"),
        "launch",
        "gemini_330_series.launch.py",
    )
    orbbec = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(orbbec_launch),
        launch_arguments={
            "color_width": "1280",
            "color_height": "720",
            "color_fps": "30",
            "color_qos": "default",
            "enable_depth": "false",
            "enable_point_cloud": "false",
            "depth_registration": "false",
        }.items(),
    )

    return LaunchDescription([apriltag_conf_arg, container, orbbec])
