from franky import *
import time

robot = Robot("172.16.0.2")
robot.relative_dynamics_factor = 0.03
# A cartesian velocity motion with linear (first argument) and angular (second argument) components
m_cv1 = CartesianVelocityMotion(Twist([0.1, 0, 0], [0, -0, 0]),Duration(2000))
m_cv7 = CartesianVelocityMotion(Twist([0.1, -0.1, 0], [0, -0, 0]),Duration(1000))

# With target elbow velocity
m_cv2 = CartesianVelocityMotion(RobotVelocity(Twist([0.2, -0.1, 0.1], [0.1, -0.1, 0.2]), elbow_velocity=-0.2))

# Cartesian velocity motions also support multiple waypoints. Unlike in cartesian position control, a cartesian velocity
# waypoint is a target velocity to be reached. This particular example first accelerates the end-effector, holds the 
# velocity for 1s, then # reverses direction for 2s, reverses direction again for 1s, and finally stops. It is important
# not to forget to stop # the robot at the end of such a sequence, as it will otherwise throw an error.
m_cv4 = CartesianVelocityWaypointMotion([
    CartesianVelocityWaypoint(Twist([0.2, -0.1, 0.1], [0.1, -0.1, 0.2]), hold_target_duration=Duration(1000)),
    CartesianVelocityWaypoint(Twist([-0.2, 0.1, -0.1], [-0.1, 0.1, -0.2]), hold_target_duration=Duration(2000)),
    CartesianVelocityWaypoint(Twist([0.2, -0.1, 0.1], [0.1, -0.1, 0.2]), hold_target_duration=Duration(1000)),
    CartesianVelocityWaypoint(Twist()),
])

# Stop the robot in cartesian velocity control mode.
m_cv6 = CartesianVelocityStopMotion()
robot.move(m_cv1, asynchronous=True)
time.sleep(1)
robot.move(m_cv7, asynchronous=True)
robot.join_motion()