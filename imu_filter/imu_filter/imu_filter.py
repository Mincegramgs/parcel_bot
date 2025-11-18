#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

class ImuDeadband(Node):
    def __init__(self):
        super().__init__('imu_deadband_filter')

        # Sub/Pub topics (edit as needed)
        self.sub = self.create_subscription(Imu, '/imu/data_raw', self.callback, 10)
        self.pub = self.create_publisher(Imu, '/imu/data_filtered', 10)

        # Deadband thresholds
        self.accel_threshold = 0.4  # m/s²
        self.gyro_threshold = 0.1  # rad/s

        self.get_logger().info('IMU deadband filter started.')

    def apply_deadband(self, val, thresh):
        return 0.0 if abs(val) < thresh else val

    def callback(self, msg: Imu):
        # Apply deadband to linear acceleration
        msg.linear_acceleration.x = self.apply_deadband(msg.linear_acceleration.x, self.accel_threshold)
        msg.linear_acceleration.y = self.apply_deadband(msg.linear_acceleration.y, self.accel_threshold)
        msg.linear_acceleration.z = 0.0
        # Apply deadband to angular velocity
        msg.angular_velocity.x = self.apply_deadband(msg.angular_velocity.x, self.gyro_threshold)
        msg.angular_velocity.y = self.apply_deadband(msg.angular_velocity.y, self.gyro_threshold)
        msg.angular_velocity.z = self.apply_deadband(msg.angular_velocity.z, self.gyro_threshold)

        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ImuDeadband()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

