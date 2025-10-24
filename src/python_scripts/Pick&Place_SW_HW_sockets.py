import os 
import time
import socket
from math import radians, degrees, pi
import numpy as np
import tkinter as tk
from robodk.robodialogs import *
from robodk.robolink import Robolink
from robodk.robomath import *

# Define relative path to the .rdk file
relative_path = "src/roboDK/Pick&Place_UR5e.rdk"
absolute_path = os.path.abspath(relative_path)

# Robot setup
RDK = Robolink()
time.sleep(4) # Wait for RoboDK to be ready
RDK.AddFile(absolute_path)
time.sleep(2) # Wait for the file to be loaded

robot = RDK.Item("UR5e")
base = RDK.Item("Use Base")
tool = RDK.Item("2FG7")
Init_target = RDK.Item("Init")
App_pick_target = RDK.Item("App_Pick")
Pick_target = RDK.Item("Pick")
App_place_target = RDK.Item("App_Place")
Place_target = RDK.Item("Place")
table = RDK.Item("Table")
cube = RDK.Item("cube")
cube.setVisible(False)
cube_POSE = Pick_target.Pose()
cube.setParent(table)  # Do not maintain the actual absolute POSE
cube.setPose(cube_POSE)
cube.setVisible(True)
robot.setPoseFrame(base)
robot.setPoseTool(tool)
robot.setSpeed(20)

# Robot Constants
ROBOT_IP = '192.168.1.4'
ROBOT_PORT = 30002
accel_mss = 1.2
speed_ms = 0.75
blend_r = 0.0
timej = 6
timel = 4
time_high=4

# URScript commands
set_tcp = "set_tcp(p[0.000000, 0.000000, 0.147000, 0.000000, 0.000000, 0.000000])" 
j1, j2, j3, j4, j5, j6 = np.radians(Init_target.Joints()).tolist()[0]
movel_Init = f"movel([{j1},{j2}, {j3}, {j4}, {j5}, {j6}],{accel_mss},{speed_ms},{time_high},{blend_r})"
j1, j2, j3, j4, j5, j6 = np.radians(App_pick_target.Joints()).tolist()[0]
movel_App_Pick = f"movel([{j1},{j2}, {j3}, {j4}, {j5}, {j6}],{accel_mss},{speed_ms},{time_high},{blend_r})"
j1, j2, j3, j4, j5, j6 = np.radians(Pick_target.Joints()).tolist()[0]
movel_Pick = f"movel([{j1},{j2}, {j3}, {j4}, {j5}, {j6}],{accel_mss},{speed_ms},{time_high},{blend_r})"
j1, j2, j3, j4, j5, j6 = np.radians(App_place_target.Joints()).tolist()[0]
movel_App_Place = f"movel([{j1},{j2}, {j3}, {j4}, {j5}, {j6}],{accel_mss},{speed_ms},{time_high},{blend_r})"
j1, j2, j3, j4, j5, j6 = np.radians(Place_target.Joints()).tolist()[0]
movel_Place = f"movel([{j1},{j2}, {j3}, {j4}, {j5}, {j6}],{accel_mss},{speed_ms},{time_high},{blend_r})"


# Check robot connection
def check_robot_port(ip, port):
    global robot_socket
    try:
        robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        robot_socket.settimeout(1)
        robot_socket.connect((ip, port))
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False
# Send URScript command
def send_ur_script(command):
    robot_socket.send((command + "\n").encode())

# Wait for robot response
def receive_response(t):
    try:
        print("Waiting time:", t)
        time.sleep(t)
    except socket.error as e:
        print(f"Error receiving data: {e}")
        exit(1)

def Init():
    print("Init")
    robot.MoveL(Init_target, True)
    print("Init_target REACHED")

    if robot_is_connected and ur5e_execution:
        print("Init REAL UR5e")
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movel_Init)
        receive_response(timel)
    else:
        print("UR5e not connected. Simulation only.")

def Pick():
    print("Pick")
    robot.MoveL(App_pick_target, True)
    print("App_pick_target REACHED")
    robot.setSpeed(10)  # Reduce speed for approach
    robot.MoveL(Pick_target, True)
    print("Pick_target REACHED")

    cube.setParentStatic(tool)  # Maintain the actual absolute POSE
    robot.MoveL(App_pick_target, True)
    print("Pick FINISHED")
    robot.setSpeed(20)  # Restore speed
    if robot_is_connected and ur5e_execution:
        print("App_pick REAL UR5e")
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movel_App_Pick)
        receive_response(timel)
        send_ur_script(movel_Pick)
        receive_response(timel*2)
        send_ur_script("set_digital_out(0, True)")  # Close gripper
        robot_socket.settimeout(1) 
        send_ur_script(movel_App_Pick)
        receive_response(timel) 


def Place():
    print("Place")
    robot.MoveL(App_place_target, True)
    print("App_place_target REACHED")
    robot.setSpeed(10)  # Reduce speed for approach
    robot.MoveL(Place_target, True)
    print("Place_target REACHED")

    cube.setParentStatic(table)  # Maintain the actual absolute POSE
    robot.MoveL(App_place_target, True)
    print("Place FINISHED")
    robot.setSpeed(20)  # Restore speed
    
    if robot_is_connected and ur5e_execution:
        print("App_place REAL UR5e")
        send_ur_script(set_tcp)
        receive_response(1)
        send_ur_script(movel_App_Place)
        receive_response(timel)
        send_ur_script(movel_Place)
        receive_response(timel*2)
        send_ur_script("set_digital_out(0, False)")  # Open gripper
        robot_socket.settimeout(1) 
        send_ur_script(movel_App_Place)
        receive_response(timel)

    #pass

# Confirmation dialog to close RoboDK
def confirm_close():
    root = tk.Tk()
    root.withdraw()
    response = messagebox.askquestion(
        "Close RoboDK",
        "Do you want to save changes before closing RoboDK?",
        icon='question'
    )
    if response == 'yes':
        RDK.Save()
        RDK.CloseRoboDK()
        print("RoboDK saved and closed.")
    else:
        RDK.CloseRoboDK()
        print("RoboDK closed without saving.")

# Main function
def main():
    global robot_is_connected, ur5e_execution
    ur5e_execution = False # Flag for UR5e execution. Only one group at True at a time.
    robot_is_connected = check_robot_port(ROBOT_IP, ROBOT_PORT)
    Init()
    Pick()
    Place()
    Init()
    if robot_is_connected:
        robot_socket.close()

if __name__ == "__main__":
    main()
#