#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int16MultiArray , Float32MultiArray
from geometry_msgs.msg import Twist 
from sensor_msgs.msg import Joy
from rclpy import qos

class Gamepad:
    def __init__(self):
        #Axes:--------------------------------------------------------
        
        self.lx : float = 0.0                   # 0: Left X-Axis
        self.ly : float = 0.0                   # 1: Left Y-Axis
        self.l2 : float = 0.0                   # 2: L2
        self.rx : float = 0.0                   # 3: Right X-Axis
        self.ry : float = 0.0                   # 4: Right Y-Axis
        self.r2 : float = 0.0                   # 5: R2
        self.dpadLeftRight : float = 0.0        # 6: Dpad Left and Right
        self.dpadUpDown : float = 0.0           # 7: Dpad Up and Down
        
        #Buttons:-------------------------------------------------------
        
        self.button_cross : float = 0.0         # 0: 
        self.button_circle : float = 0.0        # 1:
        self.button_triangle : float = 0.0      # 2:
        self.button_square : float = 0.0        # 3:
        self.l1 : float = 0.0                   # 4:
        self.r1 : float = 0.0                   # 5:
        #self.l2_logic : float = 0.0                   # 6:
        #self.r2_logic : float = 0.0                   # 7:
        self.button_share : float = 0.0         # 8:
        self.button_option : float = 0.0        # 9:
        self.button_logo : float = 0.0          # 10:
        self.PressedLeftAnalog : float = 0.0    # 11:
        self.PressedRightAnalog : float = 0.0   # 12:

        #----------------------------------------------------------------
        
        self.dribble: bool = False  
        self.previous_state = False  # Track previous button state
        
    def update_dribble(self):

        if self.button_triangle and not self.previous_triangle_state:
    
            self.dribble = not self.dribble  # Toggle state
            
        self.previous_triangle_state = self.button_triangle  # Update button state

class Joystick(Node):
    def __init__(self):
        super().__init__("joystick")

        self.pub_move = self.create_publisher(
            Twist, "/shaq/cmd_move", qos_profile=qos.qos_profile_system_default
        )
        
        self.pub_macro = self.create_publisher(
            Twist, "/shaq/cmd_macro", qos_profile=qos.qos_profile_system_default
        )

        self.pub_shoot = self.create_publisher(
            Twist, "/shaq/cmd_shoot", qos_profile=qos.qos_profile_system_default
        )
        
        self.pub_cmd_koby = self.create_publisher(
            Int16MultiArray, "shaq/cmd_koby", qos_profile=qos.qos_profile_system_default
        )

        self.create_subscription(
            Joy, '/shaq/joy', self.joy, qos_profile=qos.qos_profile_sensor_data # 10
        )

        self.gamepad = Gamepad()
        self.maxspeed : float = 1.0
        


        self.sent_data_timer = self.create_timer(0.01, self.sendData)

    def joy(self, msg):
        
        #Axes:--------------------------------------------------------
        
        self.gamepad.lx = float(msg.axes[0] * -1)                   # 0: Left X-Axis
        self.gamepad.ly = float(msg.axes[1])                        # 1: Left Y-Axis
        self.gamepad.l2 = float((msg.axes[2] + 1)/ 2)               # 2: L2
        self.gamepad.rx = float(msg.axes[3] * -1)                   # 3: Right X-Axis
        self.gamepad.ry = float(msg.axes[4])                        # 4: Right Y-Axis
        self.gamepad.r2 = float((msg.axes[5] + 1)/ 2)               # 5: R2
        self.gamepad.dpadLeftRight  = float(msg.axes[6])            # 6: Dpad Left and Right
        self.gamepad.dpadUpDown     = float(msg.axes[7])            # 7: Dpad Up and Down
        
        #Buttons:-------------------------------------------------------

        self.gamepad.button_cross    = float(msg.buttons[0])        # 0: 
        self.gamepad.button_circle   = float(msg.buttons[1])        # 1:
        self.gamepad.button_triangle = float(msg.buttons[2])        # 2:
        self.gamepad.button_square   = float(msg.buttons[3])        # 3:
        self.gamepad.l1              = float(msg.buttons[4])        # 4:
        self.gamepad.r1              = float(msg.buttons[5])        # 5:
        #self.gamepad.l2              = float(msg.buttons[6])        # 6:
        #self.gamepad.r2              = float(msg.buttons[7])        # 7:
        self.gamepad.button_share    = float(msg.buttons[8])        # 8:
        self.gamepad.button_option   = float(msg.buttons[9])        # 9:
        self.gamepad.button_logo     = float(msg.buttons[10])       # 10:
        self.gamepad.PressedLeftAnalog  = float(msg.buttons[11])    # 11:
        self.gamepad.PressedRightAnalog = float(msg.buttons[12])    # 12:
        
        
        #Macro-----------------------------------------------------------
        
        self.gamepad.update_dribble()

        
        

    def sendData(self):
        
        cmd_vel_move = Twist()
        cmd_vel_shoot = Twist()
        cmd_vel_macro = Twist()
        cmd_koby = Int16MultiArray()


        cmd_vel_move.linear.x = float(self.gamepad.lx * self.maxspeed)
        cmd_vel_move.linear.y = float(self.gamepad.ly * self.maxspeed)
        cmd_vel_move.angular.z = float(self.gamepad.rx * self.maxspeed)
        
        cmd_vel_shoot.linear.x = float(self.gamepad.r2 * self.maxspeed)
        cmd_vel_shoot.linear.y = float(self.gamepad.r2 * self.maxspeed)
        cmd_vel_shoot.linear.z = float(self.gamepad.l2 * self.maxspeed)
        cmd_vel_shoot.angular.x = float(self.gamepad.dpadUpDown * self.maxspeed)

        
        
        if self.gamepad.dribble:
            cmd_vel_macro.linear.x = 1.0
              
        else:
            cmd_vel_macro.linear.x = 0.0  
        
        cmd_koby.data = [int(self.gamepad.button_logo)]
        
        self.pub_macro.publish(cmd_vel_macro)
        self.pub_move.publish(cmd_vel_move)
        self.pub_shoot.publish(cmd_vel_shoot)
        self.pub_cmd_koby.publish(cmd_koby)


def main():
    rclpy.init()

    sub = Joystick()
    rclpy.spin(sub)
    rclpy.shutdown()

if __name__ == "__main__":
    main()
