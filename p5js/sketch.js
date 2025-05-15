let socket;
let armPosition = [0, 0, 0];
let isFirstUpdate = true;

function setup() {
    createCanvas(windowWidth, windowHeight);
    
    // 连接到服务器
    socket = io.connect('http://localhost:3000', {
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000
    });
    
    // 监听服务器发来的臂位置信息
    socket.on('armPosition', (data) => {
        if (isFirstUpdate) {
            mouseX = map(data[0][0], 0.3, 0.5, 0, width);
            mouseY = map(data[0][1], -0.1, 0.1, height, 0);
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

function draw() {
    background(0);
    
    // 蓝色圆点显示当前末端位置
    fill(0, 0, 255);
    noStroke();
    let armX = map(armPosition[0], 0.3, 0.5, 0, width);
    let armY = map(armPosition[1], -0.1, 0.1, height, 0);
    ellipse(armX, armY, 50, 50);
    
    // 红色圆点显示鼠标位置
    fill(255, 0, 0);
    noStroke();
    ellipse(mouseX, mouseY, 50, 50);

    // 发送鼠标位置到机械臂
    const targetPosition = [
        map(mouseX, 0, width, 0.3, 0.5),
        map(mouseY, height, 0, -0.1, 0.1),
        armPosition[2]
    ];
    socket.emit('updateArmPosition', targetPosition);
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
}
