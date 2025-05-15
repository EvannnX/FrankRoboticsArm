import time
from franky import *

robot = Robot("172.16.0.2")
robot.relative_dynamics_factor = 0.04

try:
    motion1 = CartesianMotion(Affine([0.2, 0.0, 0.0]), ReferenceType.Relative)
    robot.move(motion1, asynchronous=True)

    time.sleep(1)
    # 
    # Note that similar to reactions, when preempting active motions with new motions, the control mode cannot change.
    # Hence, we cannot use, e.g., a JointMotion here.
    motion2 = CartesianMotion(Affine([-0.1, -0.1, 0.0]), ReferenceType.Relative)
    robot.move(motion2, asynchronous=True)
    robot.join_motion()
except Exception as e:
    print(f"An error occurred: {e}")