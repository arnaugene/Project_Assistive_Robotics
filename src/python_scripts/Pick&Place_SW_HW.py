import os 
import time
from math import radians, degrees, pi
from robodk.robodialogs import *
from robodk.robolink import *
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

# Connect to real robot or simulate
def robot_online(online):
    print("Connecting to UR5e...")
    if online:
        robot.setConnectionParams('192.168.1.4', 30000, '/', 'anonymous', '')
        time.sleep(5)
        success = robot.ConnectSafe('192.168.1.4')
        time.sleep(5)
        status, status_msg = robot.ConnectedState()
        if status != ROBOTCOM_READY:
            raise Exception("Failed to connect: " + status_msg)
        RDK.setRunMode(RUNMODE_RUN_ROBOT)
        print("Connection to UR5e Successful!")
    else:
        RDK.setRunMode(RUNMODE_SIMULATE)
        print("Simulation mode activated.")

def Init():
    print("Init")
    robot.MoveL(Init_target, True)
    print("Init_target REACHED")

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
    
    pass


# Main function
def main():
    robot_online(False)  # True for real robot, False for simulation
    Init()
    Pick()
    Place()
    Init()

if __name__ == "__main__":
    main()
#