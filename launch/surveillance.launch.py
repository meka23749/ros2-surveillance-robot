from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='surveillance_robot',
            executable='robot_navigator',
            name='robot_navigator',
            output='screen'
        ),
        Node(
            package='surveillance_robot',
            executable='camera_sensor',
            name='camera_sensor',
            output='screen'
        ),
        Node(
            package='surveillance_robot',
            executable='anomaly_detector',
            name='anomaly_detector',
            output='screen'
        ),
        Node(
            package='surveillance_robot',
            executable='surveillance_manager',
            name='surveillance_manager',
            output='screen'
        ),
        Node(
            package='surveillance_robot',
            executable='visualizer',
            name='visualizer',
            output='screen'
        ),
        Node(
            package='surveillance_robot',
            executable='rviz_publisher',
            name='rviz_publisher',
            output='screen'
        ),
    ])
