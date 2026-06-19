const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreDisplay = document.getElementById('score');
const startButton = document.getElementById('startButton');

const gridSize = 20;
let snake = [{ x: 10, y: 10 }];
let food = {};
let direction = 'right';
let score = 0;
let gameInterval;
let isGameOver = true;
let changingDirection = false; // To prevent rapid direction changes

function generateFood() {
    food = {
        x: Math.floor(Math.random() * (canvas.width / gridSize)),
        y: Math.floor(Math.random() * (canvas.height / gridSize))
    };
    // Ensure food doesn't spawn on the snake
    for (let i = 0; i < snake.length; i++) {
        if (food.x === snake[i].x && food.y === snake[i].y) {
            generateFood();
            return;
        }
    }
}

function drawGame() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw snake
    for (let i = 0; i < snake.length; i++) {
        ctx.fillStyle = (i === 0) ? '#a2e061' : '#61dafb'; // Head color vs body color
        ctx.fillRect(snake[i].x * gridSize, snake[i].y * gridSize, gridSize, gridSize);
        ctx.strokeStyle = '#282c34';
        ctx.strokeRect(snake[i].x * gridSize, snake[i].y * gridSize, gridSize, gridSize);
    }

    // Draw food
    ctx.fillStyle = '#ff6b6b';
    ctx.fillRect(food.x * gridSize, food.y * gridSize, gridSize, gridSize);
    ctx.strokeStyle = '#282c34';
    ctx.strokeRect(food.x * gridSize, food.y * gridSize, gridSize, gridSize);
}

function moveSnake() {
    if (isGameOver) return;

    const head = { x: snake[0].x, y: snake[0].y };

    switch (direction) {
        case 'up':
            head.y--;
            break;
        case 'down':
            head.y++;
            break;
        case 'left':
            head.x--;
            break;
        case 'right':
            head.x++;
            break;
    }

    // Check for collisions
    const hitWall = head.x < 0 || head.x >= canvas.width / gridSize || head.y < 0 || head.y >= canvas.height / gridSize;
    const hitSelf = snake.some((segment, index) => index !== 0 && segment.x === head.x && segment.y === head.y);

    if (hitWall || hitSelf) {
        isGameOver = true;
        alert('Game Over! Your score: ' + score);
        startButton.textContent = 'Play Again';
        startButton.style.display = 'block';
        clearInterval(gameInterval);
        return;
    }

    snake.unshift(head);

    // Check if snake ate food
    if (head.x === food.x && head.y === food.y) {
        score++;
        scoreDisplay.textContent = 'Score: ' + score;
        generateFood();
    } else {
        snake.pop();
    }
    changingDirection = false;
}

function changeDirection(event) {
    if (changingDirection) return;
    changingDirection = true;

    const keyPressed = event.keyCode;
    const LEFT_KEY = 37;
    const UP_KEY = 38;
    const RIGHT_KEY = 39;
    const DOWN_KEY = 40;

    const goingUp = direction === 'up';
    const goingDown = direction === 'down';
    const goingLeft = direction === 'left';
    const goingRight = direction === 'right';

    if (keyPressed === LEFT_KEY && !goingRight) {
        direction = 'left';
    }
    if (keyPressed === UP_KEY && !goingDown) {
        direction = 'up';
    }
    if (keyPressed === RIGHT_KEY && !goingLeft) {
        direction = 'right';
    }
    if (keyPressed === DOWN_KEY && !goingUp) {
        direction = 'down';
    }
}

function resetGame() {
    snake = [{ x: 10, y: 10 }];
    direction = 'right';
    score = 0;
    scoreDisplay.textContent = 'Score: 0';
    isGameOver = false;
    generateFood();
    startButton.style.display = 'none';
    if (gameInterval) clearInterval(gameInterval);
    gameInterval = setInterval(() => {
        moveSnake();
        drawGame();
    }, 150); // Game speed
}

startButton.addEventListener('click', resetGame);
document.addEventListener('keydown', changeDirection);

// Initial draw
drawGame();
