#!/usr/bin/env python3

import sys
import select
import termios
import tty
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class ArrowTeleop(Node):

    def __init__(self):
        super().__init__('arrow_teleop')

        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.linear_speed = 0.1
        self.angular_speed = 0.2

    def publish(self, linear_x=0.0, angular_z=0.0):
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        self.publisher.publish(msg)


def main():

    rclpy.init()
    node = ArrowTeleop()

    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

    print()
    print("ROBILE Arrow Teleoperation")
    print()
    print("↑  Forward")
    print("↓  Backward")
    print("←  Turn left")
    print("→  Turn right")
    print("SPACE  Stop")
    print("Q      Quit")
    print()

    last_command = time.monotonic()

    try:

        while rclpy.ok():

            # Check whether a key has been pressed
            ready, _, _ = select.select(
                [sys.stdin],
                [],
                [],
                0.05
            )

            if ready:

                key = sys.stdin.read(1)

                # Arrow key
                if key == '\x1b':

                    sequence = sys.stdin.read(2)

                    if sequence == '[A':
                        # Up
                        node.publish(
                            linear_x=0.1
                        )

                    elif sequence == '[B':
                        # Down
                        node.publish(
                            linear_x=-0.1
                        )

                    elif sequence == '[C':
                        # Right
                        node.publish(
                            angular_z=-0.2
                        )

                    elif sequence == '[D':
                        # Left
                        node.publish(
                            angular_z=0.2
                        )

                    last_command = time.monotonic()

                elif key == ' ':
                    # Space = stop
                    node.publish()
                    last_command = 0

                elif key.lower() == 'q':
                    break

            # Stop automatically after 0.25 s
            if (
                last_command != 0
                and time.monotonic() - last_command > 0.25
            ):
                node.publish()
                last_command = 0

            rclpy.spin_once(node, timeout_sec=0)

    finally:

        node.publish()

        termios.tcsetattr(
            sys.stdin,
            termios.TCSADRAIN,
            old_settings
        )

        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
