let socket;
let armPosition = [0, 0, 0];
let webcam;
let handResults=undefined;
let videoElement;
let lastUpdateTime = 0;
const UPDATE_INTERVAL = 50; // 50ms
let lastValidLandmark = null;
let smoothedFingerPositions = [0, 0];
let fingerPositions = [-10, -10];
const SMOOTHING_FACTOR = 0.3;
let isGripperClosed = false;
const PINCH_THRESHOLD = 0.08;
let lastGripperCommandTime = 0;
const GRIPPER_COMMAND_INTERVAL = 300; // 300ms

function setup() {
    createCanvas(windowWidth, windowHeight);
    webcam=createCapture(VIDEO);
    webcam.size(640, 480);
    webcam.hide();
    initHandLandMarker()
    textSize(32);
    stroke(255);
    textAlign(CENTER, CENTER);
    text("Initializing...",width/2-100,height/2);
    // 连接到服务器
    socket = io.connect('http://localhost:3000', {
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000
    });
    
    // 监听服务器发来的臂位置信息
    socket.on('armPosition', (data) => {
        if (fingerPositions[0]<-5) {
            fingerPositions[0] = map(data[0][1], -0.1, 0.1, 0, width);
            fingerPositions[1] = map(data[0][2], 0.028, 0.5, height, 0);
            isFirstUpdate = false;
        }
        armPosition = data[0];
    });

    socket.on('connect', () => {
        console.log('已连接到服务器');
    });

    socket.on('connect_error', (error) => {
        console.log('连接错误:', error);
    });

    socket.on('disconnect', () => {
        console.log('与服务器断开连接');
    });

      
}

async function initHandLandMarker(){
    console.log("Initializing HandLandmarker...");
    const videoElement = document.getElementsByClassName('input_video')[0];
    const hands = new Hands({locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
      }});
      hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 0,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
      });
      hands.onResults((results)=>{
        handResults=results;
      });
      
      const camera = new Camera(videoElement, {
        onFrame: async () => {
          await hands.send({image: videoElement});
        },
        width: 640,
        height: 480
      });
      camera.start().then(() => {
        console.log('Camera started');
      }
      ).catch((error) => {
        console.error('Error starting camera:', error);
      }
      );
    console.log("HandLandmarker initialized");
}



function draw() {
    background(0);
    const currentTime = millis();
    let shouldUpdateArm = false;
    if (handResults){
        // push();
        // translate(width,0);
        // scale(-1,1);
        // image(webcam,0,0,width,height);
        // pop();
        if (handResults.multiHandLandmarks.length > 0) {
            lastValidLandmark = handResults.multiHandLandmarks;
            const rawX=width-(handResults.multiHandLandmarks[0][8].x * width);
            const rawY=handResults.multiHandLandmarks[0][8].y * height;
            smoothedFingerPositions[0] = lerp(smoothedFingerPositions[0], rawX, SMOOTHING_FACTOR);
            smoothedFingerPositions[1] = lerp(smoothedFingerPositions[1], rawY, SMOOTHING_FACTOR);
            fingerPositions[0] = smoothedFingerPositions[0];
            fingerPositions[1] = smoothedFingerPositions[1];
            const root=handResults.multiHandLandmarks[0][0];
            const thumb=handResults.multiHandLandmarks[0][4];
            const index=handResults.multiHandLandmarks[0][8];
            const distance=calculateDistance(thumb,index);
            textSize(24);
            fill(255);
            text(`Pinch: ${distance.toFixed(2)}`, 150, 50);
            checkPinchAndControlGripper(distance,currentTime);

            if (currentTime - lastUpdateTime > UPDATE_INTERVAL) {
                lastUpdateTime = currentTime;
                shouldUpdateArm = true;
            }
            push();
            translate(width,0);
            scale(-1,1);
            for (let i = 0; i < handResults.multiHandLandmarks.length; i++) {

                const landmarks = handResults.multiHandLandmarks[i];
                drawHandLandmarks(landmarks);
                drawHandConnections(landmarks);
            }
            pop();
        }
    }else{
            fill(255);
            textSize(32);
            textAlign(CENTER, CENTER);
            text("Initializing...",width/2-100,height/2);
        
    }

    textSize(24);
    fill(255);
    text(`Gripper: ${isGripperClosed ? 'Closed' : 'Open'}`, 150, 80);
    // 蓝色圆点显示当前末端位置
    fill(0, 0, 255);
    noStroke();
    let armY = map(armPosition[1], -0.1, 0.1, 0, width);
    let armZ = map(armPosition[2], -0.05, 0.5, height, 0);
    ellipse(armY, armZ, 50, 50);
    
    // 红色圆点显示鼠标位置
    fill(255, 0, 0);
    noStroke();
    ellipse(fingerPositions[0], fingerPositions[1], 50, 50);

    // 发送鼠标位置到机械臂
    const targetPosition = [
        armPosition[0],//0.3-0.5
        constrain(map(fingerPositions[0], 0, width, -0.1, 0.1),-0.1,0.1),
        constrain(map(fingerPositions[1], height, 0, -0.05, 0.5),0.028,0.5)
    ];
    socket.emit('updateArmPosition', targetPosition);
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
}


function drawHandLandmarks(landmarks) {
    for (let i = 0; i < landmarks.length; i++) {
        const landmark = landmarks[i];
        if (i===4 || i === 8) {
            fill(255, 0, 0);
            noStroke();
            circle(landmark.x * width, landmark.y * height, 15);
        } else {
            fill(0, 255, 0);
            noStroke();
            circle(landmark.x * width, landmark.y * height, 8);
        }
    }
}
function drawHandConnections(landmarks) {
    const connections = [
        [0, 1], [1, 2], [2, 3], [3, 4],
        [0, 5], [5, 6], [6, 7], [7, 8],
        [0, 9], [9, 10], [10, 11], [11, 12],
        [0, 13], [13, 14], [14, 15], [15, 16],
        [0, 17], [17, 18], [18, 19], [19, 20],
        [5, 9], [9, 13], [13, 17],
    ];
    stroke(0,255,0);
    strokeWeight(2);
    for (const [i,j] of connections) {
        const start=landmarks[i];
        const end=landmarks[j];
        line(start.x * width, start.y * height, end.x * width, end.y * height);
    }
}

function calculateDistance(point1, point2) {
    const dx = point1.x - point2.x;
    const dy = point1.y - point2.y;
    const dz = point1.z - point2.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
}

function calculateScale(point1, point2) {

}

function checkPinchAndControlGripper(distance,currentTime){
    if (currentTime-lastGripperCommandTime < GRIPPER_COMMAND_INTERVAL) {
        return;
    }
    if (distance<PINCH_THRESHOLD && !isGripperClosed) {
    isGripperClosed=true;
    socket.emit('gripperCommand',{command:'close'});
    lastGripperCommandTime = currentTime;
    console.log("Gripper closed");
    }else if (distance>=PINCH_THRESHOLD && isGripperClosed) {
        isGripperClosed=false;
        socket.emit('gripperCommand',{command:'open'});
        lastGripperCommandTime = currentTime;
        console.log("Gripper opened");
    }
}