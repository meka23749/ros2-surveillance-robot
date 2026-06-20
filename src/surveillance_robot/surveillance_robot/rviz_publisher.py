import json

import rclpy
from geometry_msgs.msg import Pose2D, Point
from rclpy.node import Node
from std_msgs.msg import String, ColorRGBA
from visualization_msgs.msg import Marker, MarkerArray


class RvizPublisher(Node):

    def __init__(self):
        super().__init__('rviz_publisher')
        self.pose_subscriber = self.create_subscription(
            Pose2D, '/robot/pose', self.pose_callback, 10)
        self.detection_subscriber = self.create_subscription(
            String, '/detection/result', self.detection_callback, 10)
        self.marker_publisher = self.create_publisher(
            MarkerArray, '/visualization/markers', 10)
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.anomaly_markers = []
        self.marker_id = 0
        self.timer = self.create_timer(0.1, self.publish_markers)
        self.get_logger().info('RViz2 Publisher started')

    def pose_callback(self, msg):
        self.robot_x = msg.x
        self.robot_y = msg.y

    def detection_callback(self, msg):
        result = json.loads(msg.data)
        if result['anomaly_found'] and result['confidence'] > 0.3:
            anomaly = {
                'x': self.robot_x,
                'y': self.robot_y,
                'confidence': result['confidence']
            }
            self.anomaly_markers.append(anomaly)
            self.get_logger().warn(
                f'Anomaly marker added at x={self.robot_x:.2f} y={self.robot_y:.2f}')

    def make_robot_marker(self):
        marker = Marker()
        marker.header.frame_id = 'map'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'robot'
        marker.id = 0
        marker.type = Marker.ARROW
        marker.action = Marker.ADD
        marker.pose.position.x = self.robot_x
        marker.pose.position.y = self.robot_y
        marker.pose.position.z = 0.0
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.3
        marker.scale.y = 0.1
        marker.scale.z = 0.1
        marker.color.r = 0.0
        marker.color.g = 0.5
        marker.color.b = 1.0
        marker.color.a = 1.0
        return marker

    def make_waypoint_markers(self):
        waypoints = [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)]
        markers = []
        for i, (x, y) in enumerate(waypoints):
            marker = Marker()
            marker.header.frame_id = 'map'
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = 'waypoints'
            marker.id = i + 1
            marker.type = Marker.CYLINDER
            marker.action = Marker.ADD
            marker.pose.position.x = x
            marker.pose.position.y = y
            marker.pose.position.z = 0.0
            marker.pose.orientation.w = 1.0
            marker.scale.x = 0.15
            marker.scale.y = 0.15
            marker.scale.z = 0.05
            marker.color.r = 0.0
            marker.color.g = 1.0
            marker.color.b = 0.0
            marker.color.a = 0.8
            markers.append(marker)
        return markers

    def make_anomaly_markers(self):
        markers = []
        for i, anomaly in enumerate(self.anomaly_markers[-10:]):
            marker = Marker()
            marker.header.frame_id = 'map'
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = 'anomalies'
            marker.id = i + 100
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.position.x = anomaly['x']
            marker.pose.position.y = anomaly['y']
            marker.pose.position.z = 0.0
            marker.pose.orientation.w = 1.0
            marker.scale.x = 0.2
            marker.scale.y = 0.2
            marker.scale.z = 0.2
            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0
            marker.color.a = 0.9
            markers.append(marker)
        return markers

    def publish_markers(self):
        marker_array = MarkerArray()
        marker_array.markers.append(self.make_robot_marker())
        marker_array.markers.extend(self.make_waypoint_markers())
        marker_array.markers.extend(self.make_anomaly_markers())
        self.marker_publisher.publish(marker_array)


def main(args=None):
    rclpy.init(args=args)
    node = RvizPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
