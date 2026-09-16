# Recipe From Ingredients

## What It Does

Recipe Finder helps you decide what to cook from ingredients already in your kitchen. Add ingredients as removable chips, then compare them with public recipe data. You can sort and filter matches, save favorites in your browser, open full recipe details, or use Surprise Me to select a random match.

## API Used

This app uses the keyless public [DummyJSON Recipes API](https://dummyjson.com/docs/recipes), specifically `https://dummyjson.com/recipes?limit=0`. It intentionally uses an endpoint that does not require a private API key, so no secret credentials are stored in this repository.

## How the API Call Works

`app.js` uses `fetch()` to send an HTTP GET request to the recipe endpoint. After checking that the response succeeded, `response.json()` converts the JSON response into JavaScript objects. The response contains a `recipes` array; this app uses fields such as `name`, `ingredients`, `instructions`, `image`, `cuisine`, `difficulty`, `mealType`, `prepTimeMinutes`, `cookTimeMinutes`, `servings`, and `rating`. The recipe list is fetched once and cached in memory, then filtering and matching happen locally.

## How to Run

Open `recipe-finder/index.html` through a local web server (for example, run `python3 -m http.server` from the repository root, then visit `http://localhost:8000/recipe-finder/`). You can also use the published GitHub Pages site. An internet connection is required to load recipes and their images from DummyJSON.

## Features

- Ingredient chips, Enter-to-add, duplicate prevention, and clear all
- Partial ingredient matching with match percentages and missing ingredients
- Sort by match, total time, or rating; filter by cuisine, difficulty, meal type, and time
- Recipe detail dialog, localStorage favorites, and Surprise Me
- Helpful loading, empty-input, no-results, and failed-request messages

## AI Tools Used

- Codex

## Known Issues

<!-- Add issues found during your own testing here. -->
