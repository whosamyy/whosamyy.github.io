# Crossy Road

This is my browser-based version of Crossy Road. It includes cars and roads, plus water with moving logs, train tracks, changing weather, and a high-score system. There are also different animals, scenery themes, and background music.

## How to Play

Click Start Game or press Space or Enter to start. Use the arrow keys or WASD to move your animal around.

The goal is to keep moving forward and cross as many lanes as possible. Your score goes up when you reach a new row.

You have to avoid cars and trucks on the road, stay on logs when crossing water, and watch out for trains. The train lights flash before the train comes, so you have a little warning.

If you get hit by a car or train, or fall into the water, the game ends. You can press R, Space, Enter, or the Play Again button to restart.

The game also keeps track of your best score.

Use the music button in the top-right corner to turn the background music on or off. It remembers your choice for the next time you play.

## Extra Features

I wanted each run to feel a little different instead of always having the same chicken and background.

- There are four scenery themes: Clover Meadow, Cherry Blossom, Autumn Orchard, and Frosty Pines. The background, grass, water, and other colors change to match the theme.
- There are ten animals: chicken, bunny, fox, panda, frog, pig, dog, bear, monkey, and penguin. I added the pig, dog, bear, monkey, and penguin after the first five. They all move and play the same way, so the difference is how they look.
- Each new run randomly picks an animal and a theme, avoiding the previous choices when browser storage is available. The game shows their names above the play area.
- I added a cute looping tune with an on/off button. The music starts after you interact with the game and pauses when you switch to another tab.
- I updated the start screen and colors to go with the new animals and scenery.

## AI Tools Used

I mainly used Kiro to help me build and debug the game. I also used ChatGPT (GPT-5.6) to plan features and organize parts of the project.

My overall strategy was to first get the basic Crossy Road gameplay working, like movement, scoring, cars, and collisions. After that, I added extra features one at a time, like logs, trains, weather, animations, and the high score system.

For the latest changes, I followed the same approach: add the scenery themes, animals, and music, then expand the animal list. I also used Codex to help update this README based on the code and commit history.

## Known Issues / Unfinished

There are no major unfinished features that I know of right now. Some parts of the game can still feel a little random depending on which lanes and weather are generated. Animals and themes are picked automatically; there isn't a menu to choose them yourself. The controls are keyboard-based, so there aren't touch controls for playing on a phone yet.
