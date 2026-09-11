// ─────────────────────────────────────────────
//  game.js  —  CMU 15-113 HW2  |  Crossy Road
// ─────────────────────────────────────────────
//
//  FILE STRUCTURE (each section will be filled in later):
//
//  1. Canvas setup          — grab the canvas and get the drawing context
//  2. Game state            — variables that track what's happening in the game
//  3. Draw functions        — functions that paint things onto the canvas
//  4. Update functions      — functions that move/change things each frame
//  5. Input handling        — keyboard/touch listeners
//  6. Game loop             — the repeating cycle: update → draw → repeat
//  7. Start / reset         — wire up the Start button
//
// ─────────────────────────────────────────────


// ── 1. Canvas setup ──────────────────────────

// getElementById finds the <canvas> tag we wrote in index.html
const canvas = document.getElementById("gameCanvas");

// getContext("2d") gives us the drawing tools (lines, rectangles, text, etc.)
const ctx = canvas.getContext("2d");

// Convenient shorthand so we don't type canvas.width everywhere
const WIDTH  = canvas.width;   // 600
const HEIGHT = canvas.height;  // 600


// ── 2. Game state ─────────────────────────────
// All the variables that describe the current state of the game.
// We'll expand this section as we add features.

let score    = 0;       // how many rows the player has crossed
let gameOver = false;   // is the game currently over?
let running  = false;   // has the player pressed Start yet?


// ── 3. Draw functions ─────────────────────────
// Each draw function is responsible for painting one thing.
// They read from game state but do NOT change it.

// Clears the whole canvas and redraws every frame
function drawBackground() {
  ctx.fillStyle = "#16213e";
  ctx.fillRect(0, 0, WIDTH, HEIGHT);
}

// Placeholder: draws a simple square where the player will be
function drawPlayer() {
  ctx.fillStyle = "#e94560";
  ctx.fillRect(280, 520, 40, 40); // (x, y, width, height)
}

// Draws everything — call this once per frame
function drawAll() {
  drawBackground();
  drawPlayer();
}


// ── 4. Update functions ───────────────────────
// These will move cars, scroll lanes, check collisions, etc.
// Empty for now — we'll add logic here next.

function updateAll() {
  // TODO: move cars
  // TODO: scroll the world upward as the player advances
  // TODO: check collisions
}


// ── 5. Input handling ─────────────────────────
// Listen for arrow key presses to move the player.

document.addEventListener("keydown", function(event) {
  if (!running) return; // ignore input before the game starts

  if (event.key === "ArrowUp")    { /* TODO: move player up    */ }
  if (event.key === "ArrowDown")  { /* TODO: move player down  */ }
  if (event.key === "ArrowLeft")  { /* TODO: move player left  */ }
  if (event.key === "ArrowRight") { /* TODO: move player right */ }
});


// ── 6. Game loop ──────────────────────────────
// requestAnimationFrame asks the browser to call our function
// ~60 times per second, in sync with screen refreshes.

function gameLoop() {
  if (!running) return;  // stop the loop if the game isn't running

  updateAll();
  drawAll();

  requestAnimationFrame(gameLoop); // schedule the next frame
}


// ── 7. Start / reset ──────────────────────────

function startGame() {
  // Reset state
  score    = 0;
  gameOver = false;
  running  = true;

  // Update the score display in the HTML
  document.getElementById("score").textContent = "Score: 0";

  // Kick off the loop
  requestAnimationFrame(gameLoop);
}

// Wire the button up — clicking "Start Game" calls startGame()
document.getElementById("startBtn").addEventListener("click", startGame);
