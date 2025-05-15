var net;
var video;
var currentResult;
var socket;
var armPosition = [0, 0, 0];
var isFirstUpdate = true;
var isModelLoaded = false;

function setup() {
  createCanvas(800, 600);
  console.log("开始初始化...");

  video = createCapture(VIDEO);
  video.elt.addEventListener('loadeddata', videoLoadedCallback);
  video.size(800, 600);
  video.hide();
  console.log("视频初始化完成");

  // 初始化Socket.IO连接
  socket = io('http://localhost:3000', {
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000
  });
  
  socket.on('connect', () => {
    console.log('已连接到服务器');
  });

  socket.on('connect_error', (error) => {
    console.error('连接错误:', error);
  });

  socket.on('disconnect', (reason) => {
    console.log('断开连接:', reason);
  });

  socket.on('armPosition', (data) => {
    console.log('收到机械臂位置:', data);
    armPosition = data[0];
  });
}

function draw() {
  background(255);
  image(video, 0, 0, 800, 600);

  // 显示调试信息
  fill(0);
  textSize(16);
  text("模型加载状态: " + (isModelLoaded ? "已加载" : "未加载"), 10, 20);
  text("检测结果: " + (currentResult ? "有" : "无"), 10, 40);

  if (currentResult) {
    var nose = currentResult.keypoints[0].position;
    var eye1 = currentResult.keypoints[1].position;
    var eye2 = currentResult.keypoints[2].position;

    // 只显示红鼻子（使用更大的圆形）
    fill(255, 0, 0);
    noStroke();
    ellipse(nose.x, nose.y, 50, 50);  // 增大红点尺寸

    var scale = (eye1.x - eye2.x) / 700;
    console.log("眼睛间距:", eye1.x - eye2.x, "缩放比例:", scale);

    // 将红鼻子位置映射到机械臂坐标系
    let mappedX = map(nose.x, 0, width, 0.0, 0.8);
    let mappedY = map(nose.y, 0, height, -0.4, 0.4);
    let mappedZ = map(nose.y, 0, height, 0.0, 0.7);

    // 显示映射后的坐标
    fill(0);
    textSize(16);
    text(`映射坐标: X=${mappedX.toFixed(3)}, Y=${mappedY.toFixed(3)}, Z=${mappedZ.toFixed(3)}`, 10, 60);

    // 发送位置到机械臂控制系统
    console.log('发送位置更新:', [mappedX, mappedY, mappedZ]);
    socket.emit('updateNosePosition', [mappedX, mappedY, mappedZ]);
  }
}

function videoLoadedCallback() {
  console.log("视频加载完成，开始加载PoseNet模型...");
  posenet.load({
    architecture: 'MobileNetV1',
    outputStride: 16,
    inputResolution: { width: 640, height: 480 },
    multiplier: 0.75
  }).then(loadedCallback).catch(err => {
    console.error("PoseNet模型加载失败:", err);
  });
}

function loadedCallback(model) {
  console.log("PoseNet模型加载成功!");
  net = model;
  isModelLoaded = true;
  net.estimateSinglePose(video.elt, {
    flipHorizontal: false
  }).then(estimateCallback).catch(err => {
    console.error("姿态估计失败:", err);
  });
}

function estimateCallback(result) {
  currentResult = result;
  if (result) {
    console.log("检测到关键点:", result.keypoints.length);
  }
  net.estimateSinglePose(video.elt, {
    flipHorizontal: false
  }).then(estimateCallback).catch(err => {
    console.error("姿态估计失败:", err);
  });
}

// 添加窗口关闭事件处理
function windowClosing() {
  socket.emit('stopArm');
} 