// ═══════════════════════════════════════════════════════════════
//  game.js  —  CMU 15-113 HW2  |  Crossy Road
// ═══════════════════════════════════════════════════════════════
//
//  SECTION MAP  (use Ctrl+F to jump):
//
//  § 1  Canvas & constants
//  § 2  World & lane generation
//  § 3  Player state & hop animation
//  § 4  Cars & logs (obstacles / platforms)
//  § 5  Draw helpers  (colours, shapes, decorations)
//  § 6  Draw lane contents
//  § 7  Draw player (blocky chicken)
//  § 8  Update logic  (move cars/logs, scroll world)
//  § 9  Collision detection
//  § 10 Input handling
//  § 11 Game loop
//  § 12 Start / Game-over / Restart
//
// ═══════════════════════════════════════════════════════════════


// ─────────────────────────────────────────────────────────────
//  § 1  Canvas & constants
// ─────────────────────────────────────────────────────────────

const canvas = document.getElementById("gameCanvas");
const ctx    = canvas.getContext("2d");

const CANVAS_W = canvas.width;   // 600
const CANVAS_H = canvas.height;  // 600

// Each lane is one tile tall; each column is one tile wide
const TILE     = 60;             // px — size of one grid cell
const COLS     = CANVAS_W / TILE; // 10 columns
const VISIBLE  = CANVAS_H / TILE; // 10 rows visible on screen

// How many lanes we generate ahead of and behind the player
const LANE_BUFFER = 6;           // extra lanes generated above the top edge

// Player starts on this lane index (0 = bottom-most lane)
const START_LANE = 2;

// Hop animation duration in milliseconds
const HOP_MS = 130;


// ─────────────────────────────────────────────────────────────
//  § 2  World & lane generation
// ─────────────────────────────────────────────────────────────

// laneTypes: what kind of terrain each lane is
const LANE_GRASS  = "grass";
const LANE_ROAD   = "road";
const LANE_WATER  = "water";
const LANE_SAFE   = "safe";   // wide safe grass strip (start / checkpoints)

// world.lanes is an array of lane objects; index 0 is the very first (bottom) lane.
// As the player moves up, we generate more lanes on top.
let world = { lanes: [], cameraRow: 0 };

// Seeded pseudo-random so each run is different but deterministic per session
let _seed = Date.now();
function rand() {
  _seed ^= _seed << 13; _seed ^= _seed >> 17; _seed ^= _seed << 5;
  return ((_seed >>> 0) / 0xFFFFFFFF);
}
function randInt(min, max) { return Math.floor(rand() * (max - min + 1)) + min; }
function randChoice(arr)   { return arr[Math.floor(rand() * arr.length)]; }

// Build one lane object
function makeLane(index) {
  // First 3 lanes are always safe grass so the player has room to orient
  if (index <= 2) {
    return { type: LANE_SAFE, index, decor: makeDecor(LANE_SAFE, index) };
  }

  // After a run of 4+ consecutive roads force a grass break
  const last4 = world.lanes.slice(-4).map(l => l.type);
  const allRoad = last4.length === 4 && last4.every(t => t === LANE_ROAD);
  const last3water = world.lanes.slice(-3).map(l => l.type);
  const allWater = last3water.length === 3 && last3water.every(t => t === LANE_WATER);

  let type;
  if (allRoad || allWater) {
    type = LANE_GRASS;
  } else {
    const roll = rand();
    if (roll < 0.38)      type = LANE_ROAD;
    else if (roll < 0.55) type = LANE_WATER;
    else                  type = LANE_GRASS;
  }

  const lane = { type, index, decor: makeDecor(type, index) };

  if (type === LANE_ROAD) {
    lane.dir      = randChoice([-1, 1]);                 // -1 = left,  1 = right
    lane.speed    = 1.2 + rand() * 2.2;                  // px per frame
    lane.vehicles = makeVehicles(lane);
  }

  if (type === LANE_WATER) {
    lane.dir    = randChoice([-1, 1]);
    lane.speed  = 0.7 + rand() * 1.0;
    lane.logs   = makeLogs(lane);
  }

  return lane;
}

// Ensure the world has enough lanes above the current camera position
function ensureLanes() {
  const needed = world.cameraRow + VISIBLE + LANE_BUFFER;
  while (world.lanes.length < needed) {
    world.lanes.push(makeLane(world.lanes.length));
  }
}

// Spawn vehicles for a road lane
function makeVehicles(lane) {
  const vehicles = [];
  const count = randInt(2, 4);
  const spacing = CANVAS_W / count;
  for (let i = 0; i < count; i++) {
    const isTruck = rand() < 0.3;
    vehicles.push({
      x:      i * spacing + rand() * (spacing * 0.5),
      w:      isTruck ? TILE * 2 : TILE * 1.4,
      h:      TILE * 0.72,
      color:  randChoice(["#e74c3c","#3498db","#f39c12","#9b59b6","#1abc9c","#e67e22"]),
      isTruck
    });
  }
  return vehicles;
}

// Spawn logs for a water lane
function makeLogs(lane) {
  const logs = [];
  const count = randInt(2, 3);
  const spacing = CANVAS_W / count;
  for (let i = 0; i < count; i++) {
    logs.push({
      x: i * spacing + rand() * (spacing * 0.3),
      w: TILE * (1.8 + rand() * 1.2),
      h: TILE * 0.6
    });
  }
  return logs;
}

// Decorative objects placed on grass/safe lanes
function makeDecor(type, index) {
  if (type === LANE_ROAD || type === LANE_WATER) return [];
  const items = [];
  const count = randInt(1, 3);
  const used  = new Set();
  for (let i = 0; i < count; i++) {
    let col;
    do { col = randInt(0, COLS - 1); } while (used.has(col));
    used.add(col);
    const kind = randChoice(["tree","bush","flower","rock"]);
    items.push({ col, kind });
  }
  return items;
}


// ─────────────────────────────────────────────────────────────
//  § 3  Player state & hop animation
// ─────────────────────────────────────────────────────────────

let player = {};

// Resets the player to the starting position
function resetPlayer() {
  player = {
    col:      Math.floor(COLS / 2),  // start in the middle column
    row:      START_LANE,            // start lane index
    maxRow:   START_LANE,            // furthest row reached (for score)

    // Visual position (used for smooth hop animation)
    drawX:    0,   // set properly after reset
    drawY:    0,

    // Hop animation state
    hopping:  false,
    hopStartX: 0,
    hopStartY: 0,
    hopEndX:   0,
    hopEndY:   0,
    hopT:      0,     // 0→1 progress through the hop
    hopMs:     HOP_MS,

    dead:     false,
    onLog:    null    // reference to the log the player is standing on
  };
  syncDrawPos();
}

// Convert grid (col, row) to canvas (x, y) — top-left of the tile
function tileToScreen(col, row) {
  // row 0 is the bottom; camera scrolls up as the player advances
  const screenRow = row - world.cameraRow;
  return {
    x: col * TILE,
    y: (VISIBLE - 1 - screenRow) * TILE
  };
}

// Snap the draw position to the grid without animation
function syncDrawPos() {
  const pos    = tileToScreen(player.col, player.row);
  player.drawX = pos.x;
  player.drawY = pos.y;
}

// Start a hop from current position to (newCol, newRow)
function startHop(newCol, newRow) {
  if (player.hopping || player.dead) return;

  // Boundary checks — stay inside the grid
  if (newCol < 0 || newCol >= COLS) return;
  if (newRow < 0) return;

  const start = tileToScreen(player.col, player.row);
  const end   = tileToScreen(newCol, newRow);

  player.hopping   = true;
  player.hopStartX = start.x;
  player.hopStartY = start.y;
  player.hopEndX   = end.x;
  player.hopEndY   = end.y;
  player.hopT      = 0;

  // Commit the grid position immediately
  player.col = newCol;
  player.row = newRow;
  player.onLog = null;   // re-evaluate after hop lands

  // Track furthest row for scoring
  if (player.row > player.maxRow) {
    player.maxRow = player.row;
    updateScore(player.maxRow - START_LANE);
  }

  // Scroll the camera to keep the player in the lower third
  const idealCamera = player.row - Math.floor(VISIBLE * 0.65);
  if (idealCamera > world.cameraRow) {
    world.cameraRow = idealCamera;
    ensureLanes();
  }
}

// Advance the hop animation by dt milliseconds
function tickHop(dt) {
  if (!player.hopping) return;

  player.hopT += dt / player.hopMs;
  if (player.hopT >= 1) {
    player.hopT  = 1;
    player.hopping = false;
  }

  // Ease-out cubic for smooth deceleration
  const t = 1 - Math.pow(1 - player.hopT, 3);

  player.drawX = player.hopStartX + (player.hopEndX - player.hopStartX) * t;
  // Arc: add a vertical bounce (sin curve peaks at t=0.5)
  const arc    = Math.sin(player.hopT * Math.PI) * (TILE * 0.45);
  player.drawY = player.hopStartY + (player.hopEndY - player.hopStartY) * t - arc;
}


// ─────────────────────────────────────────────────────────────
//  § 4  Cars & logs update
// ─────────────────────────────────────────────────────────────

// Move all vehicles and logs; called once per frame
function updateObstacles(dt) {
  const speedMult = 1 + (score * 0.015);  // gradually speed up with score

  for (const lane of world.lanes) {
    if (lane.type === LANE_ROAD) {
      for (const v of lane.vehicles) {
        v.x += lane.dir * lane.speed * speedMult * (dt / 16);
        // Wrap around when they leave the screen
        if (lane.dir === 1  && v.x >  CANVAS_W + v.w)  v.x = -v.w;
        if (lane.dir === -1 && v.x < -v.w)              v.x =  CANVAS_W + v.w;
      }
    }

    if (lane.type === LANE_WATER) {
      for (const log of lane.logs) {
        log.x += lane.dir * lane.speed * (dt / 16);
        if (lane.dir === 1  && log.x >  CANVAS_W + log.w) log.x = -log.w;
        if (lane.dir === -1 && log.x < -log.w)            log.x =  CANVAS_W + log.w;
      }
    }
  }
}

// If the player is on a log, carry them sideways
function carryPlayerOnLog() {
  const lane = world.lanes[player.row];
  if (!lane || lane.type !== LANE_WATER) { player.onLog = null; return; }

  const px   = player.col * TILE + TILE / 2;
  const py   = TILE / 2;  // centre of tile — used only for hitbox
  let found  = null;

  for (const log of lane.logs) {
    const sy = tileToScreen(0, player.row).y;
    const logY = sy + (TILE - log.h) / 2;
    if (px >= log.x && px <= log.x + log.w) {
      found = log;
      break;
    }
  }

  if (found) {
    player.onLog = found;
    // Drift the player's draw position with the log between hops
    if (!player.hopping) {
      const lane2 = world.lanes[player.row];
      const speedMult = 1;
      player.drawX += lane2.dir * lane2.speed * speedMult * (1 / 60) * (1000 / 16);
      // Clamp so the player doesn't silently leave the screen on the log
      player.drawX = Math.max(-TILE * 0.3, Math.min(CANVAS_W - TILE * 0.7, player.drawX));
      // Update logical col to match drift
      player.col = Math.round(player.drawX / TILE);
      player.col = Math.max(0, Math.min(COLS - 1, player.col));
    }
  } else {
    // Player is over water with no log → die
    if (!player.hopping) {
      triggerDeath();
    }
  }
}


// ─────────────────────────────────────────────────────────────
//  § 5  Draw helpers
// ─────────────────────────────────────────────────────────────

// Colours for each lane type
const LANE_COLORS = {
  [LANE_SAFE]:  ["#52b788", "#40916c"],   // alternating shades of green
  [LANE_GRASS]: ["#52b788", "#40916c"],
  [LANE_ROAD]:  ["#495057", "#343a40"],
  [LANE_WATER]: ["#1971c2", "#1864ab"],
};

// Rounded-rectangle helper
function roundRect(x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

// Draw a single blocky vehicle (car or truck)
function drawVehicle(v, screenY) {
  const bodyH  = v.h;
  const bodyY  = screenY + (TILE - bodyH) / 2;

  // Drop shadow
  ctx.fillStyle = "rgba(0,0,0,0.25)";
  roundRect(v.x + 4, bodyY + 6, v.w, bodyH, 7);
  ctx.fill();

  // Body
  ctx.fillStyle = v.color;
  roundRect(v.x, bodyY, v.w, bodyH, 7);
  ctx.fill();

  // Roof (darker shade, inset)
  ctx.fillStyle = shadeColor(v.color, -25);
  const roofInset = v.isTruck ? 4 : 6;
  roundRect(v.x + roofInset, bodyY + 3, v.w - roofInset * 2, bodyH * 0.45, 4);
  ctx.fill();

  // Wheels (4 small dark circles)
  const wheelR = 5;
  const wheelY = bodyY + bodyH - 2;
  ctx.fillStyle = "#222";
  for (const wx of [v.x + 10, v.x + v.w - 12]) {
    ctx.beginPath();
    ctx.arc(wx, wheelY, wheelR, 0, Math.PI * 2);
    ctx.fill();
    // Hubcap
    ctx.fillStyle = "#aaa";
    ctx.beginPath();
    ctx.arc(wx, wheelY, wheelR * 0.45, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#222";
  }

  // Headlights / taillights
  const lightY = bodyY + bodyH * 0.25;
  const lightH = bodyH * 0.28;
  // Front
  ctx.fillStyle = "#fffde7";
  ctx.fillRect(v.x + v.w - 5, lightY, 5, lightH);
  // Rear
  ctx.fillStyle = "#c0392b";
  ctx.fillRect(v.x, lightY, 5, lightH);
}

// Draw one log
function drawLog(log, screenY) {
  const logY = screenY + (TILE - log.h) / 2;

  // Shadow
  ctx.fillStyle = "rgba(0,0,0,0.2)";
  roundRect(log.x + 3, logY + 5, log.w, log.h, 8);
  ctx.fill();

  // Main log body — wood brown
  ctx.fillStyle = "#8B5E3C";
  roundRect(log.x, logY, log.w, log.h, 8);
  ctx.fill();

  // Wood grain lines
  ctx.strokeStyle = "#6b4423";
  ctx.lineWidth = 1.5;
  const grainCount = Math.floor(log.w / 18);
  for (let i = 1; i < grainCount; i++) {
    const gx = log.x + (log.w / grainCount) * i;
    ctx.beginPath();
    ctx.moveTo(gx, logY + 3);
    ctx.lineTo(gx, logY + log.h - 3);
    ctx.stroke();
  }

  // Bark ends
  ctx.fillStyle = "#6b4423";
  roundRect(log.x, logY, 10, log.h, 8);
  ctx.fill();
  roundRect(log.x + log.w - 10, logY, 10, log.h, 8);
  ctx.fill();
}

// Draw decorative grass objects
function drawDecor(item, screenX, screenY) {
  const cx = screenX + TILE / 2;
  const cy = screenY + TILE * 0.7;

  if (item.kind === "tree") {
    // Trunk
    ctx.fillStyle = "#795548";
    ctx.fillRect(cx - 4, cy - 10, 8, 16);
    // Canopy layers
    ctx.fillStyle = "#2e7d32";
    ctx.beginPath(); ctx.arc(cx, cy - 18, 14, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#388e3c";
    ctx.beginPath(); ctx.arc(cx - 5, cy - 12, 10, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(cx + 5, cy - 12, 10, 0, Math.PI * 2); ctx.fill();
    // Highlight
    ctx.fillStyle = "#43a047";
    ctx.beginPath(); ctx.arc(cx - 3, cy - 22, 6, 0, Math.PI * 2); ctx.fill();

  } else if (item.kind === "bush") {
    ctx.fillStyle = "#388e3c";
    ctx.beginPath(); ctx.arc(cx,     cy - 6, 10, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(cx - 8, cy - 2, 8,  0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(cx + 8, cy - 2, 8,  0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#43a047";
    ctx.beginPath(); ctx.arc(cx - 2, cy - 9, 5,  0, Math.PI * 2); ctx.fill();

  } else if (item.kind === "flower") {
    // Stem
    ctx.strokeStyle = "#4caf50";
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx, cy - 12); ctx.stroke();
    // Petals
    const petalColors = ["#e91e63","#ff9800","#ffeb3b","#9c27b0","#03a9f4"];
    ctx.fillStyle = randChoice(petalColors);
    for (let a = 0; a < Math.PI * 2; a += Math.PI / 3) {
      ctx.beginPath();
      ctx.arc(cx + Math.cos(a) * 5, cy - 12 + Math.sin(a) * 5, 4, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.fillStyle = "#fff176";
    ctx.beginPath(); ctx.arc(cx, cy - 12, 3.5, 0, Math.PI * 2); ctx.fill();

  } else if (item.kind === "rock") {
    ctx.fillStyle = "#78909c";
    roundRect(cx - 9, cy - 8, 18, 12, 5);
    ctx.fill();
    ctx.fillStyle = "#90a4ae";
    roundRect(cx - 6, cy - 10, 10, 7, 4);
    ctx.fill();
  }
}

// Road lane markings (dashed centre line)
function drawRoadMarkings(screenY) {
  ctx.strokeStyle = "#ffee58";
  ctx.lineWidth = 2;
  ctx.setLineDash([TILE * 0.4, TILE * 0.35]);
  ctx.beginPath();
  ctx.moveTo(0,        screenY + TILE / 2);
  ctx.lineTo(CANVAS_W, screenY + TILE / 2);
  ctx.stroke();
  ctx.setLineDash([]);
}

// Water ripple lines
function drawWaterRipples(screenY, offset) {
  ctx.strokeStyle = "rgba(255,255,255,0.12)";
  ctx.lineWidth = 1.5;
  for (let i = 0; i < 3; i++) {
    const rx = ((offset * 0.3 + i * 80) % (CANVAS_W + 40)) - 20;
    ctx.beginPath();
    ctx.moveTo(rx, screenY + TILE * 0.35 + i * 8);
    ctx.bezierCurveTo(rx + 15, screenY + TILE * 0.3, rx + 25, screenY + TILE * 0.4, rx + 40, screenY + TILE * 0.35);
    ctx.stroke();
  }
}

// Darken or lighten a hex color by amount (-255 to +255)
function shadeColor(hex, amount) {
  const num = parseInt(hex.slice(1), 16);
  const r = Math.min(255, Math.max(0, (num >> 16) + amount));
  const g = Math.min(255, Math.max(0, ((num >> 8) & 0xff) + amount));
  const b = Math.min(255, Math.max(0, (num & 0xff) + amount));
  return "#" + ((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1);
}


// ─────────────────────────────────────────────────────────────
//  § 6  Draw lane contents
// ─────────────────────────────────────────────────────────────

// Running offset for water ripple animation
let rippleOffset = 0;

function drawLane(lane, screenY) {
  const colors = LANE_COLORS[lane.type];
  // Alternating stripe colour based on lane index
  ctx.fillStyle = colors[lane.index % 2];
  ctx.fillRect(0, screenY, CANVAS_W, TILE);

  if (lane.type === LANE_ROAD) {
    drawRoadMarkings(screenY);
    for (const v of lane.vehicles) {
      drawVehicle(v, screenY);
    }
  }

  if (lane.type === LANE_WATER) {
    drawWaterRipples(screenY, rippleOffset);
    for (const log of lane.logs) {
      drawLog(log, screenY);
    }
  }

  if (lane.type === LANE_GRASS || lane.type === LANE_SAFE) {
    for (const item of lane.decor) {
      const sx = item.col * TILE;
      drawDecor(item, sx, screenY);
    }
  }
}

function drawAllLanes() {
  // Draw from bottom to top so decorations on lower lanes appear behind upper ones
  for (let r = world.cameraRow; r < world.cameraRow + VISIBLE; r++) {
    const lane = world.lanes[r];
    if (!lane) continue;
    const screenY = (VISIBLE - 1 - (r - world.cameraRow)) * TILE;
    drawLane(lane, screenY);
  }
}


// ─────────────────────────────────────────────────────────────
//  § 7  Draw player (blocky chicken)
// ─────────────────────────────────────────────────────────────

function drawPlayer() {
  const x = player.drawX;
  const y = player.drawY;

  // Pixel offsets within the tile to make the chicken centred
  const bx = x + 8;
  const by = y + 6;
  const bw = TILE - 16;
  const bh = TILE - 14;

  // Drop shadow (ellipse on the ground)
  const shadowY = x !== player.hopEndX || y !== player.hopEndY
    ? player.hopEndY + TILE - 10    // shadow stays at destination during hop
    : y + TILE - 10;
  ctx.fillStyle = "rgba(0,0,0,0.22)";
  ctx.beginPath();
  ctx.ellipse(x + TILE / 2, shadowY, bw * 0.55, 5, 0, 0, Math.PI * 2);
  ctx.fill();

  if (player.dead) {
    // Death pose — X eyes, tilted
    ctx.save();
    ctx.translate(x + TILE / 2, y + TILE / 2);
    ctx.rotate(0.5);
    drawChickenBody(0 - TILE / 2 + 8, 0 - TILE / 2 + 6, bw, bh, true);
    ctx.restore();
    return;
  }

  drawChickenBody(bx, by, bw, bh, false);
}

function drawChickenBody(bx, by, bw, bh, dead) {
  // Body — white rounded block
  ctx.fillStyle = dead ? "#e0e0e0" : "#fff8e1";
  roundRect(bx, by, bw, bh, 8);
  ctx.fill();

  // Body shading (right side darker)
  ctx.fillStyle = dead ? "#bdbdbd" : "#ffe082";
  roundRect(bx + bw * 0.55, by + 4, bw * 0.38, bh - 8, 6);
  ctx.fill();

  // Wing
  ctx.fillStyle = dead ? "#9e9e9e" : "#ffd54f";
  roundRect(bx + bw * 0.1, by + bh * 0.35, bw * 0.25, bh * 0.35, 4);
  ctx.fill();

  // Head — sits on top
  const headW = bw * 0.65;
  const headH = bh * 0.52;
  const headX = bx + (bw - headW) / 2;
  const headY = by - headH * 0.65;
  ctx.fillStyle = dead ? "#e0e0e0" : "#fff8e1";
  roundRect(headX, headY, headW, headH, 7);
  ctx.fill();

  // Comb (red)
  ctx.fillStyle = "#e53935";
  ctx.beginPath();
  ctx.arc(headX + headW * 0.45, headY - 2, 4, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(headX + headW * 0.62, headY,     3, 0, Math.PI * 2);
  ctx.fill();

  // Beak
  ctx.fillStyle = "#ffb300";
  ctx.beginPath();
  ctx.moveTo(headX + headW - 2, headY + headH * 0.5);
  ctx.lineTo(headX + headW + 7, headY + headH * 0.45);
  ctx.lineTo(headX + headW - 2, headY + headH * 0.65);
  ctx.closePath();
  ctx.fill();

  // Eyes
  if (dead) {
    // X eyes
    ctx.strokeStyle = "#555";
    ctx.lineWidth = 2;
    const ex = headX + headW * 0.35;
    const ey = headY + headH * 0.35;
    ctx.beginPath(); ctx.moveTo(ex - 3, ey - 3); ctx.lineTo(ex + 3, ey + 3); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(ex + 3, ey - 3); ctx.lineTo(ex - 3, ey + 3); ctx.stroke();
  } else {
    ctx.fillStyle = "#1a1a1a";
    ctx.beginPath();
    ctx.arc(headX + headW * 0.35, headY + headH * 0.38, 3.5, 0, Math.PI * 2);
    ctx.fill();
    // Eye shine
    ctx.fillStyle = "#fff";
    ctx.beginPath();
    ctx.arc(headX + headW * 0.32, headY + headH * 0.32, 1.3, 0, Math.PI * 2);
    ctx.fill();
  }

  // Feet
  ctx.strokeStyle = "#fb8c00";
  ctx.lineWidth = 2.5;
  ctx.lineCap = "round";
  const footY = by + bh;
  // Left foot
  ctx.beginPath();
  ctx.moveTo(bx + bw * 0.25, footY);
  ctx.lineTo(bx + bw * 0.18, footY + 6);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(bx + bw * 0.25, footY);
  ctx.lineTo(bx + bw * 0.28, footY + 7);
  ctx.stroke();
  // Right foot
  ctx.beginPath();
  ctx.moveTo(bx + bw * 0.7, footY);
  ctx.lineTo(bx + bw * 0.63, footY + 6);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(bx + bw * 0.7, footY);
  ctx.lineTo(bx + bw * 0.73, footY + 7);
  ctx.stroke();
}


// ─────────────────────────────────────────────────────────────
//  § 8  Update logic
// ─────────────────────────────────────────────────────────────

let lastTimestamp = 0;

function updateAll(timestamp) {
  const dt = Math.min(timestamp - lastTimestamp, 50); // cap at 50ms to avoid spiral
  lastTimestamp = timestamp;

  rippleOffset += dt * 0.05;

  tickHop(dt);
  updateObstacles(dt);

  if (!player.dead) {
    const lane = world.lanes[player.row];
    if (lane && lane.type === LANE_WATER) {
      carryPlayerOnLog();
    }
    checkCollisions();
  }
}


// ─────────────────────────────────────────────────────────────
//  § 9  Collision detection
// ─────────────────────────────────────────────────────────────

function checkCollisions() {
  if (player.hopping || player.dead) return;

  const lane = world.lanes[player.row];
  if (!lane) return;

  // Shrink the hitbox slightly so it forgives near-misses (feels fair)
  const margin = 6;
  const px1 = player.drawX + margin;
  const px2 = player.drawX + TILE - margin;

  if (lane.type === LANE_ROAD) {
    for (const v of lane.vehicles) {
      if (px2 > v.x + margin && px1 < v.x + v.w - margin) {
        triggerDeath();
        return;
      }
    }
  }

  // Water death is handled in carryPlayerOnLog()
}

function triggerDeath() {
  if (player.dead) return;
  player.dead = true;

  // Show game-over screen after a short delay (so the death pose is visible)
  setTimeout(showGameOver, 700);
}


// ─────────────────────────────────────────────────────────────
//  § 10 Input handling
// ─────────────────────────────────────────────────────────────

document.addEventListener("keydown", function(e) {
  // Start / restart shortcuts
  if (!running) {
    if (e.key === "Enter" || e.key === " ") startGame();
    return;
  }
  if (gameOver) {
    if (e.key === "r" || e.key === "R" || e.key === "Enter" || e.key === " ") restartGame();
    return;
  }

  // Prevent arrow keys from scrolling the page
  if (["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," "].includes(e.key)) {
    e.preventDefault();
  }

  const col = player.col;
  const row = player.row;

  if (e.key === "ArrowUp"    || e.key === "w" || e.key === "W") startHop(col,     row + 1);
  if (e.key === "ArrowDown"  || e.key === "s" || e.key === "S") startHop(col,     row - 1);
  if (e.key === "ArrowLeft"  || e.key === "a" || e.key === "A") startHop(col - 1, row);
  if (e.key === "ArrowRight" || e.key === "d" || e.key === "D") startHop(col + 1, row);
});

// Touch / swipe support for mobile
let touchStartX = 0;
let touchStartY = 0;

canvas.addEventListener("touchstart", function(e) {
  touchStartX = e.touches[0].clientX;
  touchStartY = e.touches[0].clientY;
  e.preventDefault();
}, { passive: false });

canvas.addEventListener("touchend", function(e) {
  const dx = e.changedTouches[0].clientX - touchStartX;
  const dy = e.changedTouches[0].clientY - touchStartY;
  const absDx = Math.abs(dx);
  const absDy = Math.abs(dy);
  if (Math.max(absDx, absDy) < 10) return; // tap — ignore

  const col = player.col;
  const row = player.row;

  if (absDx > absDy) {
    if (dx > 0) startHop(col + 1, row);
    else        startHop(col - 1, row);
  } else {
    if (dy < 0) startHop(col,     row + 1);
    else        startHop(col,     row - 1);
  }
  e.preventDefault();
}, { passive: false });


// ─────────────────────────────────────────────────────────────
//  § 11 Game loop
// ─────────────────────────────────────────────────────────────

let running  = false;
let gameOver = false;
let score    = 0;
let highScore = parseInt(localStorage.getItem("crossy_highscore") || "0", 10);
let loopId   = null;   // requestAnimationFrame handle

function gameLoop(timestamp) {
  if (!running) return;

  updateAll(timestamp);

  // ── Draw ──
  // Clear
  ctx.clearRect(0, 0, CANVAS_W, CANVAS_H);

  // Lanes
  drawAllLanes();

  // Player (drawn on top of lanes, below UI)
  drawPlayer();

  // Request next frame
  loopId = requestAnimationFrame(gameLoop);
}


// ─────────────────────────────────────────────────────────────
//  § 12 Start / Game-over / Restart
// ─────────────────────────────────────────────────────────────

// Show the best score in the HUD
function refreshHUD() {
  document.getElementById("hudScore").textContent = "Score: " + score;
  document.getElementById("hudBest").textContent  = "Best: "  + highScore;
}

// Called whenever the score changes
function updateScore(newScore) {
  score = newScore;
  if (score > highScore) {
    highScore = score;
    localStorage.setItem("crossy_highscore", highScore);
  }
  refreshHUD();
}

function startGame() {
  // Re-seed random for a fresh world each run
  _seed = Date.now();

  // Build a fresh world
  world = { lanes: [], cameraRow: 0 };
  ensureLanes();

  // Reset player
  resetPlayer();

  // Reset state
  score    = 0;
  gameOver = false;
  running  = true;
  lastTimestamp = 0;

  refreshHUD();

  // Show game wrapper, hide overlays
  document.getElementById("startScreen").classList.add("hidden");
  document.getElementById("gameOverScreen").classList.add("hidden");
  document.getElementById("gameWrapper").classList.remove("hidden");

  // Kick off the loop
  if (loopId) cancelAnimationFrame(loopId);
  loopId = requestAnimationFrame(gameLoop);
}

function showGameOver() {
  running  = false;
  gameOver = true;

  // Do one final draw so the death pose is visible
  ctx.clearRect(0, 0, CANVAS_W, CANVAS_H);
  drawAllLanes();
  drawPlayer();

  document.getElementById("finalScore").textContent = score;
  document.getElementById("finalBest").textContent  = highScore;
  document.getElementById("gameOverScreen").classList.remove("hidden");
}

function restartGame() {
  document.getElementById("gameOverScreen").classList.add("hidden");
  startGame();
}

// Wire up buttons
document.getElementById("startBtn").addEventListener("click",   startGame);
document.getElementById("restartBtn").addEventListener("click", restartGame);
