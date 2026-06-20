import json

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String


class Visualizer(Node):

    def __init__(self):
        super().__init__('visualizer')
        self.image_subscriber = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        self.detection_subscriber = self.create_subscription(
            String, '/detection/result', self.detection_callback, 10)
        self.bridge = CvBridge()
        self.latest_detection = None
        self.get_logger().info('Visualizer started — opening display window')

    def detection_callback(self, msg):
        self.latest_detection = json.loads(msg.data)

    def image_callback(self, msg):
        img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (640, 50), (30, 30, 30), -1)
        cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)

        if self.latest_detection:
            anomaly = self.latest_detection['anomaly_found']
            confidence = self.latest_detection['confidence']

            if anomaly:
                color = (0, 0, 255)
                status = f'ANOMALY DETECTED - confidence: {confidence:.2f}'
                cv2.rectangle(img, (0, 0), (640, 480), (0, 0, 255), 4)

                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                lower_red = np.array([0, 100, 100])
                upper_red = np.array([10, 255, 255])
                mask = cv2.inRange(hsv, lower_red, upper_red)
                lower_red2 = np.array([160, 100, 100])
                upper_red2 = np.array([180, 255, 255])
                mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
                mask = cv2.bitwise_or(mask, mask2)
                contours, _ = cv2.findContours(
                    mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    if cv2.contourArea(contour) > 500:
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)
                        cv2.putText(img, f'DEFECT ({confidence:.2f})',
                                    (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                color = (0, 255, 0)
                status = 'System OK - No anomaly'

            cv2.putText(img, status, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.putText(img, 'ROS2 Surveillance System', (400, 470),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow('Industrial Surveillance Camera', img)
        cv2.waitKey(1)

    def destroy_node(self):
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = Visualizer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
