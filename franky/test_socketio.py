import math
from scipy.spatial.transform import Rotation
from franky import *
import socketio
import eventlet
import time



robot = Robot("172.16.0.2")
robot.relative_dynamics_factor = 0.01

# create a socketio server
sio=socketio.Server(cors_allowed_origins=['http://127.0.0.1:5500'])
app=socketio.WSGIApp(sio)



execute_times = 0

@sio.on('updateArmPosition')#to register a function to be called when a client sends a 'command' event
def updateArmPosition(sid, data):
    global execute_times
    execute_times += 1
    print("Received command:", data)
    execute_cartesian_position_control(data)
    sio.emit('armPosition', get_cartesian_position_endeffector(), room=sid)
    # time.sleep(0.1)

@sio.event
def stopArm(sid):
    print("Stopping robot...")
    m_cp6 = CartesianStopMotion()
    robot.move(m_cp6)
    sio.emit('armPosition', get_cartesian_position_endeffector(), room=sid)

@sio.on('connect') 
def connect(sid, environ):
    print("Client connected:", sid)
    sio.emit('armPosition', get_cartesian_position_endeffector(), room=sid)

@sio.event
def disconnect(sid):
    print("Client disconnected:", sid)



# # ------------- Joint Position Control -------------
# print("Executing Joint Position Control...")

# m_jp1 = JointMotion([-0.3, 0.1, 0.3, -1.4, 0.1, 1.8, 0.7])
# robot.move(m_jp1)

# # 稍微等待一下，避免指令堆叠太快（不是必须的，但建议加）
# import time
# time.sleep(1)

# # ------------- Joint Velocity Control -------------
# print("Executing Joint Velocity Control...")

# m_jv1 = JointVelocityMotion([0.1, 0.3, -0.1, 0.0, 0.1, -0.2, 0.4], duration=Duration(1000))
# robot.move(m_jv1)

# time.sleep(1)

# ------------- Cartesian Position Control -------------
def get_cartesian_position_endeffector():
    cartesian_state_pose_end_effector = robot.current_cartesian_state.pose.end_effector_pose
    t= cartesian_state_pose_end_effector.translation.tolist()
    p= cartesian_state_pose_end_effector.quaternion.tolist()
    # return [t]
    return [t,p]

def execute_cartesian_position_control(data):
    print("Executing Cartesian Position Control...")
    # quat = Rotation.from_euler("xyz", [0, 0, math.pi / 2]).as_quat()
    # m_cp1 = CartesianMotion(Affine(data, quat))
    print(data,'data')
    m_cp1 = CartesianMotion(Affine(data), ReferenceType.Relative)
    
    robot.move(m_cp1)
    # time.sleep(1)
print (robot.current_cartesian_state)
# print("Executing Cartesian Position Control...")

# quat = Rotation.from_euler("xyz", [0, 0, math.pi / 2]).as_quat()
# m_cp1 = CartesianMotion(Affine([0.4, -0.2, 0.3], quat))
# robot.move(m_cp1)

# time.sleep(1)

# # ------------- Cartesian Velocity Control -------------
# print("Executing Cartesian Velocity Control...")

# m_cv1 = CartesianVelocityMotion(Twist([0.2, -0.1, 0.1], [0.1, -0.1, 0.2]))
# robot.move(m_cv1)

# time.sleep(1)

# # ------------- 全部执行完毕 -------------
# print("All motions executed.")

if __name__ == '__main__':
    # run the socketio server
    eventlet.wsgi.server(eventlet.listen(('localhost', 3000)), app)
