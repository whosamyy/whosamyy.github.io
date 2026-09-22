# Recipe From Ingredients

Recipe Finder helps you decide what to cook from ingredients already in your kitchen. Its existing interface supports ingredient chips, recipe cards, filters, sorting, details, favorites, and Surprise Me.

## Backend connection

The frontend sends `POST https://recipe-finder-backend-o6bk.onrender.com/recommend` with `Content-Type: application/json` and a JSON body such as:

```json
{"ingredients":["chicken","rice","garlic"],"limit":100}
```

The separate Flask backend fetches DummyJSON recipes, matches ingredients, and returns ranked recommendations. The supported `limit: 100` gives the existing local filters a broader result set. Cuisine, difficulty, meal type, maximum time, and saved-only filters operate on those returned recommendations. Sorting by best match preserves backend order; time and rating sorting operate locally. No ingredient matching runs in the frontend.

The response must contain `success: true`, an `ingredients` array, and a `recipes` array. Cards use the backend's `matchedIngredients`, `missingIngredients`, `matchCount`, and `matchPercentage`. Recipe details use the full recipe fields returned by the backend. Favorites retain the existing localStorage key and numeric recipe IDs.

## Loading and errors

Add ingredients individually with Enter/Add ingredient, or enter a comma-separated list and choose Find recipes. Empty input is rejected before sending a request. Searches display “Finding recipes... The server may take a few seconds to wake up.” and allow up to two minutes before showing a retry message. Editing ingredient chips or clearing the form cancels stale requests.

Network errors, unsuccessful HTTP responses, backend error objects, invalid JSON, and incomplete recipe data show readable messages. Empty recommendations display the existing no-results state. No secrets or credentials are required; only the public backend URL is configured.

## Run and test

Run `python3 -m http.server 8000` from the repository root and visit `http://localhost:8000/recipe-finder/`. The backend must allow that origin for local testing and `https://whosamyy.github.io` for GitHub Pages.

After reviewing, committing, pushing, and waiting for GitHub Pages deployment, hard-refresh <https://whosamyy.github.io/recipe-finder/>. In browser developer tools, check Network for a POST to the Render `/recommend` endpoint with a successful JSON response. Try `chicken, rice, garlic`, `rice`, several ingredients, empty input, and `zzzxxyyqq`. Test recipe details, hearts and Saved only, Surprise Me, each filter, and each sort. Use the browser's offline mode to check the network error message, then restore the connection and retry. Check Console for unexpected errors.

The backend and its HW4 prompt log remain separate. Copy the full connection-request prompt verbatim into the backend repository's `prompt_log.md` as another Key Prompt; do not summarize it or create a second HW4 log here.

## AI Tools Used

- Codex
