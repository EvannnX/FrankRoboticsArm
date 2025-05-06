import math
from scipy.spatial.transform import Rotation
from franky import *

# Move to the given target pose
quat = Rotation.from_euler("xyz", [0, 0, math.pi / 2]).as_quat()
m_cp1 = CartesianMotion(Affine([0.4, -0.2, 0.3], quat))

# With target elbow angle (otherwise, the Franka firmware will choose by itself)
m_cp2 = CartesianMotion(RobotPose(Affine([0.4, -0.2, 0.3], quat), elbow_state=ElbowState(0.3)))

# A linear motion in cartesian space relative to the initial position
# (Note that this motion is relative both in position and orientation. Hence, when the robot's end-effector is oriented
# differently, it will move in a different direction)
m_cp3 = CartesianMotion(Affine([0.2, 0.0, 0.0]), ReferenceType.Relative)

# Generalization of CartesianMotion that allows for multiple waypoints
m_cp4 = CartesianWaypointMotion([
    CartesianWaypoint(RobotPose(Affine([0.4, -0.2, 0.3], quat), elbow_state=ElbowState(0.3))),
    # The following waypoint is relative to the prior one and 50% slower
    CartesianWaypoint(Affine([0.2, 0.0, 0.0]), ReferenceType.Relative, RelativeDynamicsFactor(0.5, 1.0, 1.0))
])

# Cartesian waypoints also permit to specify target velocities
m_cp5 = CartesianWaypointMotion([
    CartesianWaypoint(Affine([0.5, -0.2, 0.3], quat)),
    CartesianWaypoint(
        CartesianState(
            pose=Affine([0.4, -0.1, 0.3], quat),
            velocity=Twist([-0.01, 0.01, 0.0]))),
    CartesianWaypoint(Affine([0.3, 0.0, 0.3], quat))
])

# Stop the robot in cartesian position control mode.
m_cp6 = CartesianStopMotion()