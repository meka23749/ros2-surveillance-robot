import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
import numpy as np
import cv2
from cv_bridge import CvBridge
import json


class AnomalyDetector(Node):

    def __init__(self):
        super().__init__('anomaly_detector')
        self.image_subscriber = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        self.result_publisher = self.create_publisher(String, '/detection/result', 10)
        self.bridge = CvBridge()
        self.get_logger().info('Anomaly Detector started')

    def detect_anomaly(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)

        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask, mask2)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        anomaly_found = False
        confidence = 0.0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:
                anomaly_found = True
                confidence = min(1.0, area / 3000.0)
                break

        return anomaly_found, confidence

    def image_callback(self, msg):
        img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        anomaly_found, confidence = self.detect_anomaly(img)

        result = {
            'anomaly_found': anomaly_found,
            'confidence': round(confidence, 3),
            'timestamp': self.get_clock().now().to_msg().sec
        }

        result_msg = String()
        result_msg.data = json.dumps(result)
        self.result_publisher.publish(result_msg)

        if anomaly_found:
            self.get_logger().warn(
                f'ANOMALY DETECTED — confidence: {confidence:.2f}')
        else:
            self.get_logger().info('No anomaly detected')


def main(args=None):
    rclpy.init(args=args)
    node = AnomalyDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
