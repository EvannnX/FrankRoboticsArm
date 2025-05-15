import math
from scipy.spatial.transform import Rotation
from franky import *
import socketio
import eventlet
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建机器人实例
try:
    robot = Robot("172.16.0.2")
    robot.relative_dynamics_factor = 0.03
    logger.info("机器人连接成功")
except Exception as e:
    logger.error(f"机器人连接失败: {e}")
    exit(1)

# 创建socketio服务器
sio = socketio.Server(
    cors_allowed_origins=['http://127.0.0.1:5500', 'http://localhost:5500'],
    logger=True,
    engineio_logger=True
)
app = socketio.WSGIApp(sio)

# 运动控制相关变量
last_command_time = 0
command_interval = 0.1  # 命令发送间隔（秒）

def get_cartesian_position_endeffector():
    try:
        cartesian_state_pose_end_effector = robot.current_cartesian_state.pose.end_effector_pose
        t = cartesian_state_pose_end_effector.translation.tolist()
        p = cartesian_state_pose_end_effector.quaternion.tolist()
        logger.info(f"获取位置成功: {t}")
        return [t, p]
    except Exception as e:
        logger.error(f"获取位置失败: {e}")
        return [[0, 0, 0], [0, 0, 0, 1]]

def execute_cartesian_position_control(data):
    global last_command_time
    current_time = time.time()
    
    # 检查命令发送间隔
    if current_time - last_command_time < command_interval:
        return
    
    try:
        logger.info(f"执行笛卡尔位置控制: {data}")
        quat = Rotation.from_euler("xyz", [math.pi, 0, 0]).as_quat()
        m_cp1 = CartesianMotion(Affine(data, quat))
        robot.move(m_cp1, asynchronous=True)
        last_command_time = current_time
    except Exception as e:
        logger.error(f"执行运动失败: {e}")

@sio.on('updateArmPosition')
def updateArmPosition(sid, data):
    try:
        execute_cartesian_position_control(data)
        sio.emit('armPosition', get_cartesian_position_endeffector(), room=sid)
    except Exception as e:
        logger.error(f"更新位置失败: {e}")

@sio.event
def stopArm(sid):
    try:
        logger.info("停止机器人...")
        m_cp6 = CartesianStopMotion()
        robot.move(m_cp6)
        sio.emit('armPosition', get_cartesian_position_endeffector(), room=sid)
    except Exception as e:
        logger.error(f"停止失败: {e}")

@sio.on('connect')
def connect(sid, environ):
    logger.info(f"客户端连接: {sid}")
    try:
        sio.emit('armPosition', get_cartesian_position_endeffector(), room=sid)
    except Exception as e:
        logger.error(f"发送初始位置失败: {e}")

@sio.event
def disconnect(sid):
    logger.info(f"客户端断开连接: {sid}")
    try:
        robot.join_motion()
    except Exception as e:
        logger.error(f"断开连接处理失败: {e}")

if __name__ == '__main__':
    logger.info("启动服务器在 localhost:3000...")
    try:
        eventlet.wsgi.server(eventlet.listen(('localhost', 3000)), app)
    except Exception as e:
        logger.error(f"服务器启动失败: {e}") 