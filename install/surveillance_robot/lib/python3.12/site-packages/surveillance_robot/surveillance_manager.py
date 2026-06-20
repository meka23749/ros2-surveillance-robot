import json

from geometry_msgs.msg import Pose2D
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SurveillanceManager(Node):

    def __init__(self):
        super().__init__('surveillance_manager')
        self.detection_subscriber = self.create_subscription(
            String, '/detection/result', self.detection_callback, 10)
        self.pose_subscriber = self.create_subscription(
            Pose2D, '/robot/pose', self.pose_callback, 10)
        self.command_publisher = self.create_publisher(String, '/robot/command', 10)
        self.current_pose = None
        self.anomaly_count = 0
        self.total_detections = 0
        self.robot_stopped = False
        self.get_logger().info('Surveillance Manager started')

    def pose_callback(self, msg):
        self.current_pose = msg

    def detection_callback(self, msg):
        result = json.loads(msg.data)
        self.total_detections += 1
        if result['anomaly_found'] and result['confidence'] > 0.3:
            self.anomaly_count += 1
            command = String()
            command.data = 'STOP'
            self.command_publisher.publish(command)
            self.robot_stopped = True
            pos_info = ''
            if self.current_pose:
                pos_info = (
                    f' at x={self.current_pose.x:.2f}'
                    f' y={self.current_pose.y:.2f}')
            self.get_logger().warn(
                f'AUTONOMOUS DECISION: STOP robot{pos_info} - '
                f'anomaly confidence={result["confidence"]:.2f} '
                f'(total anomalies: {self.anomaly_count})')
        elif self.robot_stopped and not result['anomaly_found']:
            command = String()
            command.data = 'CONTINUE'
            self.command_publisher.publish(command)
            self.robot_stopped = False
            self.get_logger().info(
                'AUTONOMOUS DECISION: CONTINUE patrol - zone clear')
        rate = (self.anomaly_count / self.total_detections * 100
                if self.total_detections > 0 else 0)
        self.get_logger().info(
            f'Stats: {self.anomaly_count}/{self.total_detections} '
            f'anomalies detected ({rate:.1f}%)')


def main(args=None):
    rclpy.init(args=args)
    node = SurveillanceManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
