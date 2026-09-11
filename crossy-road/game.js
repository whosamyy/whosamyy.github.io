// AI assistance: Codex helped implement this plain JavaScript starter game.
// Positions use grid spaces, not pixels, so the board can resize with the page.
const board = document.getElementById("game-container");
const scoreDisplay = document.getElementById("score");
const statusDisplay = document.getElementById("game-status");
const restartButton = document.getElementById("restart-button");
const columns = 9;
const rows = 11;
const playerSize = 0.65;
const carWidth = 1.5;
const carHeight = 0.7;

// A positive speed moves right; a negative speed moves left (spaces per second).
const roads = [
    { row: 1, speed: 1.6 },
    { row: 2, speed: -2 },
    { row: 4, speed: 1.4 },
    { row: 5, speed: -1.8 },
    { row: 7, speed: 1.7 },
    { row: 8, speed: -1.3 }
];
let player;
let playerElement;
let cars = [];
let bestRow;
let gameOver = false;
let animationId;
let lastTime;

// Turn a grid rectangle into percentage-based CSS coordinates.
function positionElement(element, x, y, width, height) {
    element.style.left = (x / columns * 100) + "%";
    element.style.top = (y / rows * 100) + "%";
    element.style.width = (width / columns * 100) + "%";
    element.style.height = (height / rows * 100) + "%";
}

function drawPlayer() {
    const inset = (1 - playerSize) / 2;
    positionElement(playerElement, player.column + inset, player.row + inset,
        playerSize, playerSize);
}

// Restart cancels the old animation and rebuilds all state and board elements.
function startGame() {
    cancelAnimationFrame(animationId);
    board.replaceChildren();
    cars = [];
    player = { column: 4, row: rows - 1 };
    bestRow = player.row;
    gameOver = false;
    lastTime = null;
    scoreDisplay.textContent = "0";
    statusDisplay.textContent = "Cross the roads and reach the top!";

    roads.forEach(function (road) {
        const lane = document.createElement("div");
        lane.className = "road";
        positionElement(lane, 0, road.row, columns, 1);
        board.appendChild(lane);

        // Two spaced-out cars per road leave gaps for the player to cross.
        [0, 5].forEach(function (x) {
            const element = document.createElement("div");
            element.className = "car";
            const car = { x: x, row: road.row, speed: road.speed, element: element };
            cars.push(car);
            board.appendChild(element);
            positionElement(element, x, road.row + 0.15, carWidth, carHeight);
        });
    });

    playerElement = document.createElement("div");
    playerElement.className = "player";
    playerElement.textContent = "●";
    board.appendChild(playerElement);
    drawPlayer();
    animationId = requestAnimationFrame(updateGame);
}

// Rectangles collide when their horizontal AND vertical ranges overlap.
// We check the visible shapes, not the whole grid cell around the player.
function checkCollision() {
    const inset = (1 - playerSize) / 2;
    const playerX = player.column + inset;
    const playerY = player.row + inset;
    const hit = cars.some(function (car) {
        const carY = car.row + 0.15;
        return playerX < car.x + carWidth &&
            playerX + playerSize > car.x &&
            playerY < carY + carHeight &&
            playerY + playerSize > carY;
    });
    if (hit) {
        gameOver = true;
        statusDisplay.textContent = "Game Over";
        cancelAnimationFrame(animationId);
    }
}

// requestAnimationFrame calls this before the browser paints its next frame.
// Elapsed seconds keep cars at the same speed on different refresh-rate screens.
function updateGame(time) {
    if (gameOver) return;
    const seconds = lastTime === null ? 0 : Math.min((time - lastTime) / 1000, 0.05);
    lastTime = time;

    cars.forEach(function (car) {
        car.x += car.speed * seconds;
        // Wrap only after the entire car has left the board.
        if (car.x > columns) car.x = -carWidth;
        if (car.x < -carWidth) car.x = columns;
        positionElement(car.element, car.x, car.row + 0.15, carWidth, carHeight);
    });
    checkCollision();
    if (!gameOver) animationId = requestAnimationFrame(updateGame);
}

// Each key press moves exactly one space. Holding a key does not repeat moves.
const moves = {
    arrowup: [0, -1], w: [0, -1],
    arrowdown: [0, 1], s: [0, 1],
    arrowleft: [-1, 0], a: [-1, 0],
    arrowright: [1, 0], d: [1, 0]
};
document.addEventListener("keydown", function (event) {
    const move = moves[event.key.toLowerCase()];
    if (!move || event.ctrlKey || event.metaKey || event.altKey) return;
    event.preventDefault(); // Arrow keys should move the player, not scroll the page.
    if (gameOver || event.repeat) return;

    // Clamp coordinates so the player cannot leave any edge of the board.
    player.column = Math.max(0, Math.min(columns - 1, player.column + move[0]));
    player.row = Math.max(0, Math.min(rows - 1, player.row + move[1]));
    drawPlayer();
    checkCollision(); // Also detect moving directly into a car between frames.
    if (gameOver) return;

    // Only a new farthest-forward row earns points; backtracking earns nothing.
    bestRow = Math.min(bestRow, player.row);
    scoreDisplay.textContent = String(rows - 1 - bestRow);
    if (player.row === 0) {
        gameOver = true;
        statusDisplay.textContent = "You made it! Press Restart to play again.";
        cancelAnimationFrame(animationId);
    }
});

restartButton.addEventListener("click", startGame);
startGame();
