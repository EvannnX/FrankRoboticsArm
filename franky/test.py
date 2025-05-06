import math
from scipy.spatial.transform import Rotation
from franky import *

# 连接机器人（请替换成你自己的IP）
robot = Robot("172.16.0.2")

# 设置动态参数（让动作慢一点，安全）
robot.relative_dynamics_factor = 0.05

# ------------- Joint Position Control -------------
print("Executing Joint Position Control...")

m_jp1 = JointMotion([-0.3, 0.1, 0.3, -1.4, 0.1, 1.8, 0.7])
robot.move(m_jp1)

# 稍微等待一下，避免指令堆叠太快（不是必须的，但建议加）
import time
time.sleep(1)

# ------------- Joint Velocity Control -------------
print("Executing Joint Velocity Control...")

m_jv1 = JointVelocityMotion([0.1, 0.3, -0.1, 0.0, 0.1, -0.2, 0.4], duration=Duration(1000))
robot.move(m_jv1)

time.sleep(1)

# ------------- Cartesian Position Control -------------
print("Executing Cartesian Position Control...")

quat = Rotation.from_euler("xyz", [0, 0, math.pi / 2]).as_quat()
m_cp1 = CartesianMotion(Affine([0.4, -0.2, 0.3], quat))
robot.move(m_cp1)

time.sleep(1)

# ------------- Cartesian Velocity Control -------------
print("Executing Cartesian Velocity Control...")

m_cv1 = CartesianVelocityMotion(Twist([0.2, -0.1, 0.1], [0.1, -0.1, 0.2]))
robot.move(m_cv1)

time.sleep(1)

# ------------- 全部执行完毕 -------------
print("All motions executed.")
