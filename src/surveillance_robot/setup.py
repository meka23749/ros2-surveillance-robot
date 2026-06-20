from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'surveillance_robot'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('../../launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Steve Meka',
    maintainer_email='steve@example.com',
    description='Autonomous industrial surveillance robot with ROS2 Jazzy',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'robot_navigator = surveillance_robot.robot_navigator:main',
            'camera_sensor = surveillance_robot.camera_sensor:main',
            'anomaly_detector = surveillance_robot.anomaly_detector:main',
            'surveillance_manager = surveillance_robot.surveillance_manager:main',
            'visualizer = surveillance_robot.visualizer:main',
            'rviz_publisher = surveillance_robot.rviz_publisher:main',
        ],
    },
)
