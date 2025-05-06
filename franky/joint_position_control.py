from franky import *

# A point-to-point motion in the joint space
m_jp1 = JointMotion([-0.3, 0.1, 0.3, -1.4, 0.1, 1.8, 0.7])

# A motion in joint space with multiple waypoints
m_jp2 = JointWaypointMotion([
    JointWaypoint([-0.3, 0.1, 0.3, -1.4, 0.1, 1.8, 0.7]),
    JointWaypoint([0.0, 0.3, 0.3, -1.5, -0.2, 1.5, 0.8]),
    JointWaypoint([0.1, 0.4, 0.3, -1.4, -0.3, 1.7, 0.9])
])

# Intermediate waypoints also permit to specify target velocities. The default target velocity is 0, meaning that the
# robot will stop at every waypoint.
m_jp3 = JointWaypointMotion([
    JointWaypoint([-0.3, 0.1, 0.3, -1.4, 0.1, 1.8, 0.7]),
    JointWaypoint(
        JointState(
            position=[0.0, 0.3, 0.3, -1.5, -0.2, 1.5, 0.8],
            velocity=[0.1, 0.0, 0.0, 0.0, -0.0, 0.0, 0.0])),
    JointWaypoint([0.1, 0.4, 0.3, -1.4, -0.3, 1.7, 0.9])
])

# Stop the robot in joint position control mode. The difference of JointStopMotion to other stop motions such as 
# CartesianStopMotion is that # JointStopMotion # stops the robot in joint position control mode while 
# CartesianStopMotion stops it in cartesian pose control mode. The difference becomes relevant when asynchronous move 
# commands are being sent or reactions are being used(see below).
m_jp4 = JointStopMotion()