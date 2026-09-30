# Recipe From Ingredients

Recipe Finder helps you decide what to cook from ingredients already in your kitchen. Its existing interface supports ingredient chips, recipe cards, filters, sorting, details, favorites, and Surprise Me.

## Backend connection

The frontend sends `POST https://recipe-finder-backend-o6bk.onrender.com/recommend` with `Content-Type: application/json` and a JSON body such as:

```json
{"ingredients":["chicken","rice","garlic"],"limit":100}
```

The separate Flask backend fetches DummyJSON recipes, matches ingredients, and returns ranked recommendations. The supported `limit: 100` gives the existing local filters a broader result set. Cuisine, difficulty, meal type, maximum time, and saved-only filters operate on those returned recommendations. Sorting by best match preserves backend order; time and rating sorting operate locally. No ingredient matching runs in the frontend.

The response must contain `success: true`, an `ingredients` array, and a `recipes` array. Cards use the backend's `matchedIngredients`, `missingIngredients`, `matchCount`, and `matchPercentage`. Recipe details use the full recipe fields returned by the backend. Favorites use the SQLite API described below; browser storage contains only an anonymous client ID.

## Loading and errors

Add ingredients individually with Enter/Add ingredient, or enter a comma-separated list and choose Find recipes. Empty input is rejected before sending a request. Searches display “Finding recipes... The server may take a few seconds to wake up.” and allow up to two minutes before showing a retry message. Editing ingredient chips or clearing the form cancels stale requests.

Network errors, unsuccessful HTTP responses, backend error objects, invalid JSON, and incomplete recipe data show readable messages. Empty recommendations display the existing no-results state. No secrets or credentials are required; only the public backend URL is configured.

## Run and test

Run `python3 -m http.server 8000` from the repository root and visit `http://localhost:8000/recipe-finder/`. The backend must allow that origin for local testing and `https://whosamyy.github.io` for GitHub Pages.

After reviewing, committing, pushing, and waiting for GitHub Pages deployment, hard-refresh <https://whosamyy.github.io/recipe-finder/>. In browser developer tools, check Network for a POST to the Render `/recommend` endpoint with a successful JSON response. Try `chicken, rice, garlic`, `rice`, several ingredients, empty input, and `zzzxxyyqq`. Test recipe details, hearts and Saved only, Surprise Me, each filter, and each sort. Use the browser's offline mode to check the network error message, then restore the connection and retry. Check Console for unexpected errors.

The backend lives in the separate `recipe-finder-backend` repository. This Saved Recipes request is recorded verbatim as a new Key Prompt in both repositories.

## AI Tools Used

- Codex

## SQLite Saved Recipes

Favorites are stored by the backend, not in browser storage. The browser stores only a random `recipe-finder-client-id` UUID; clearing browser storage loses access to that anonymous collection. IDs are not authentication: anyone who knows an ID can access its collection. Old local-only favorite IDs are removed; they did not contain complete recipes and must be saved again.

The server creates `favorites.sqlite3` and the table automatically at startup, including when imported by Gunicorn. Set `DATABASE_PATH` to override the file location; missing parent directories are created. Relative paths resolve from the server working directory. SQLite is part of Python's standard library.

```sql
CREATE TABLE favorites (
  client_id TEXT NOT NULL,
  recipe_id INTEGER NOT NULL,
  recipe_name TEXT NOT NULL,
  image_url TEXT NOT NULL,
  ingredients TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  PRIMARY KEY (client_id, recipe_id)
);
```

`ingredients` contains a JSON array of strings; `created_at` is a UTC timestamp. The composite primary key prevents duplicate saves per client. All values use parameterized SQL. Connections are closed after each operation and writes are transactional.

| Method | Endpoint | Response |
| --- | --- | --- |
| POST | `/favorites` with `{ "clientId": "<UUID>", "recipe": { "id": 1, "name": "Rice", "image": "https://example.com/rice.jpg", "ingredients": ["Rice"] } }` | 201 for a new save; 200 for an existing save, unchanged. `{success: true, created: boolean, favorite: {...}}` |
| GET | `/favorites?clientId=<UUID>` | 200 `{success: true, favorites: [...]}`, newest first; empty array when none |
| DELETE | `/favorites/1?clientId=<UUID>` | 200 `{success: true, recipeId: 1}`; 404 if absent for that client |

Returned favorites contain `id`, `name`, `image`, `ingredients`, and `createdAt`. Invalid input returns 400, oversized bodies 413, and database failures 503, all with `{success: false, error: "..."}`. Client IDs must be UUIDs. Recipe IDs must be positive safe integers; names have 1–200 characters; image URLs must use HTTP(S) and be at most 2048 characters; ingredients require 1–100 nonblank strings, each at most 500 characters. The existing 16 KiB body limit still applies. CORS permits DELETE as well as GET and POST for the existing allowed origins.

### Local setup

In the separate `recipe-finder-backend` repository:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
DATABASE_PATH=/tmp/recipe-finder-tests.sqlite3 python -m unittest -v
DATABASE_PATH=./data/favorites.sqlite3 PORT=5001 python app.py
```

In the frontend repository, run `python3 -m http.server 8000` and open `http://localhost:8000/recipe-finder/`. The frontend automatically uses `http://127.0.0.1:5001` on localhost/127.0.0.1, and the existing Render URL in production. Search, save, reload, inspect Saved Recipes, then unsave. Saved only still filters the current search results. The collection shows saved names, images, and ingredients independently of search. Refresh saved recipes retries failures and picks up changes from another tab. Search, details, filters, sorting, and Surprise Me retain their existing behavior.

### Deployment and persistence

Deploy the backend changes before deploying the frontend on GitHub Pages. Existing build/start commands remain `pip install -r requirements.txt` and `gunicorn app:app`. No API keys or new Python packages are needed. Database files and SQLite journals are ignored by Git; never commit these files or secrets.

Render's free filesystem is ephemeral: the SQLite file may not persist after a restart or redeployment. For durable saves, use a paid Render service with a persistent disk mounted, for example, at `/var/data`, and set `DATABASE_PATH=/var/data/favorites.sqlite3` in the Render environment. Setting the variable alone does not provide persistence; the file must be inside the disk mount. Keep this SQLite deployment on one service instance and arrange database backups. See [Render persistent disks](https://render.com/docs/disks).

### Automated browser verification

With backend dependencies and `playwright` installed in your Python environment and Google Chrome installed, run `python recipe-finder/tests/browser_flow.py` from the frontend repository. The test expects the backend in the sibling `recipe-finder-backend` directory (override with `BACKEND_DIR`) and free ports 8000/5001. It creates a temporary database and runs real Flask HTTP requests; only DummyJSON recommendations are stubbed. It checks save/reload/unsave, separate clients, existing search controls, mobile overflow, storage contents, and network/server error recovery. A mobile screenshot is written to `/tmp/recipe-saved-mobile.png`.

Verified on September 30, 2026: all 13 backend tests passed, including all 10 existing recommendation tests; the Chrome integration flow passed with no JavaScript exceptions. Production deployment remains a manual step.
