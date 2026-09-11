# Prompt Log

Tool: OpenAI Codex (GPT-6).

## Setup Prompt

```text
I am working inside my existing GitHub Pages repository called whosamyy.github.io.

Set up the folder structure for my CMU 15-113 HW2 Crossy Road project.

Do NOT create a new Git repository.

Inside the current repo, create a folder named:

crossy-road

Inside that folder, create these files:

index.html
style.css
game.js
README.md
prompt\_log.md

Do not add advanced game code yet. Just create a clean starter structure.

For index.html:

- include the standard HTML boilerplate
- set the page title to "Crossy Road"
- link style.css
- include game.js using defer
- add a simple main container with:
  - an h1 saying "Crossy Road"
  - a score display
  - a game container/div
  - a restart button

For style.css:

- add only very basic starter styling so the page is centered and readable
- do not spend time on detailed design yet

For game.js:

- add a short comment saying this file will contain the game logic
- add a console.log("Crossy Road loaded");

For README.md:

- add a heading "HW2 - Crossy Road"
- briefly say this is my CMU 15-113 HW2 browser game

For prompt\_log.md:

- add a heading "Prompt Log"
- add a section called "Setup Prompt"
- paste this entire prompt under that section verbatim

After creating everything, show me the final file tree and briefly tell me what files you created. Do not commit or push anything to GitHub yet.

```

## Minimum Playable Version

Tool: OpenAI Codex (GPT-6).

```text
Now build the minimum playable version of the Crossy Road game.

Keep everything as plain HTML, CSS, and JavaScript so it works directly on GitHub Pages with no npm, server, or build step.

Use the existing files:

- index.html
- style.css
- game.js

Implement only the core gameplay for now:

1. Create a visible game board inside #game-container.
2. Add a simple player character near the bottom of the board.
3. Let the player move one space at a time using:
   - ArrowUp / W
   - ArrowDown / S
   - ArrowLeft / A
   - ArrowRight / D
4. Add several horizontal road lanes.
5. Add cars that continuously move left or right across those lanes.
6. Detect collisions between the player and cars.
7. If the player is hit:
   - stop the game
   - display "Game Over"
   - allow the Restart button to start a new game
8. Increase the score when the player moves farther forward.
9. Prevent the player from moving outside the game board.

Keep the code beginner-readable and organized. Do not add rivers, logs, trains, sound effects, libraries, or complicated 3D graphics yet.

Add clear comments explaining the main parts of game.js because I need to understand and explain the code.

Do not commit or push anything.

After making the changes:

- tell me which files you changed
- explain briefly how movement, collision detection, scoring, and restart work
- tell me exactly how to test the game in my browser
```
