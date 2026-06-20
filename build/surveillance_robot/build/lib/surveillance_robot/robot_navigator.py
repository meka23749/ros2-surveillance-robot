import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose2D
from std_msgs.msg import String
import math
import time


WAYPOINTS = [
    (0.0, 0.0),
    (2.0, 0.0),
    (2.0, 2.0),
    (0.0, 2.0),
]


class RobotNavigator(Node):

    def __init__(self):
        super().__init__('robot_navigator')
        self.pose_publisher = self.create_publisher(Pose2D, '/robot/pose', 10)
        self.command_subscriber = self.create_subscription(
            String, '/robot/command', self.command_callback, 10)
        self.current_waypoint = 0
        self.x = 0.0
        self.y = 0.0
        self.paused = False
        self.timer = self.create_timer(0.5, self.navigate)
        self.get_logger().info('Robot Navigator started')

    def command_callback(self, msg):
        if msg.data == 'STOP':
            self.paused = True
            self.get_logger().warn('Robot STOPPED — anomaly detected!')
        elif msg.data == 'CONTINUE':
            self.paused = False
            self.get_logger().info('Robot CONTINUING patrol')

    def navigate(self):
        if self.paused:
            return

        target_x, target_y = WAYPOINTS[self.current_waypoint]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)

        if dist < 0.1:
            self.current_waypoint = (self.current_waypoint + 1) % len(WAYPOINTS)
            self.get_logger().info(
                f'Reached waypoint {self.current_waypoint} — moving to next')
        else:
            speed = 0.1
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed

        pose = Pose2D()
        pose.x = self.x
        pose.y = self.y
        pose.theta = math.atan2(dy, dx) if dist > 0.01 else 0.0
        self.pose_publisher.publish(pose)
        self.get_logger().info(f'Position: x={self.x:.2f} y={self.y:.2f}')


def main(args=None):
    rclpy.init(args=args)
    node = RobotNavigator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
