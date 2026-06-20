import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Pose2D
import numpy as np
import cv2
from cv_bridge import CvBridge
import random


class CameraSensor(Node):

    def __init__(self):
        super().__init__('camera_sensor')
        self.image_publisher = self.create_publisher(Image, '/camera/image_raw', 10)
        self.pose_subscriber = self.create_subscription(
            Pose2D, '/robot/pose', self.pose_callback, 10)
        self.bridge = CvBridge()
        self.current_pose = None
        self.timer = self.create_timer(1.0, self.publish_image)
        self.get_logger().info('Camera Sensor started')

    def pose_callback(self, msg):
        self.current_pose = msg

    def generate_scene(self):
        img = np.ones((480, 640, 3), dtype=np.uint8) * 200

        cv2.rectangle(img, (50, 50), (590, 430), (150, 150, 150), 2)
        cv2.putText(img, 'Industrial Zone', (200, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)

        num_objects = random.randint(2, 5)
        for _ in range(num_objects):
            x = random.randint(80, 560)
            y = random.randint(80, 400)
            cv2.circle(img, (x, y), 20, (0, 180, 0), -1)

        anomaly = random.random() < 0.3
        if anomaly:
            ax = random.randint(100, 500)
            ay = random.randint(100, 380)
            pts = np.array([
                [ax, ay],
                [ax + 40, ay + 10],
                [ax + 20, ay + 50],
                [ax - 10, ay + 30]
            ], np.int32)
            cv2.fillPoly(img, [pts], (0, 0, 220))
            cv2.putText(img, 'ANOMALY', (ax - 10, ay - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        if self.current_pose:
            info = f'Robot: x={self.current_pose.x:.1f} y={self.current_pose.y:.1f}'
            cv2.putText(img, info, (10, 460),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 50, 50), 1)

        return img, anomaly

    def publish_image(self):
        img, anomaly = self.generate_scene()
        msg = self.bridge.cv2_to_imgmsg(img, encoding='bgr8')
        self.image_publisher.publish(msg)
        status = 'ANOMALY in scene' if anomaly else 'Normal scene'
        self.get_logger().info(f'Published image — {status}')


def main(args=None):
    rclpy.init(args=args)
    node = CameraSensor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
