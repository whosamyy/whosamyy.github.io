# Prompt Log

## Tools Used

- Codex

## Key Prompts

I am working on CMU 15-113 HW3: Explore an API.

I want to build a useful and polished "Recipe From Ingredients" web app inside my EXISTING GitHub Pages repository, whosamyy.github.io.

Do NOT create a new Git repository.

Create a new folder inside the existing repository named:

recipe-finder

Inside it, create:

- index.html
- style.css
- app.js
- README.md
- prompt_log.md

The finished app must work directly on GitHub Pages using plain HTML, CSS, and JavaScript. Do NOT use React, npm, Vite, a backend, or a build step.

==================================================
SECURITY / PRIVACY — THIS IS EXTREMELY IMPORTANT
==================================================

My assignment has a strict privacy requirement.

DO NOT put any private API key, access token, password, credential, secret, or other sensitive value anywhere in this repository.

Specifically:

- Never put a private API key in index.html.
- Never put a private API key in app.js.
- Never put a private API key in a URL.
- Never put a private API key in README.md.
- Never put a private API key in prompt_log.md.
- Never commit .env or config files containing secrets.
- Never hardcode credentials in browser-side JavaScript.

A private key in frontend JavaScript is NOT secure, even if it is placed in a separate config file, because anyone can inspect browser code and network requests.

For this project, use a KEYLESS PUBLIC API so that the app can safely run on GitHub Pages.

Use the public DummyJSON Recipes API:
https://dummyjson.com/recipes

According to its documentation, the public recipe endpoints can be fetched without authentication. Do not use any authenticated DummyJSON endpoints.

If you discover that anything we want to use requires a private key, token, authentication, paid API key, or other secret:
STOP.
Do not add the credential.
Tell me that the feature cannot safely be implemented in a frontend-only GitHub Pages project.

Even though this project should not need secrets, create/update the repository .gitignore to include common secret files such as:

.env
.env.*
config.local
secrets.json

Do not overwrite any existing useful .gitignore entries.

Before finishing, search the files you created and make sure there are no API keys, tokens, credentials, passwords, or secrets.

If a private key were ever accidentally committed, deleting it in a later commit would NOT be enough because it would remain in Git history. The key would need to be revoked/regenerated immediately.

==================================================
APP IDEA
==================================================

The app should help someone answer:

"What can I cook with the ingredients I already have?"

The user should be able to enter multiple ingredients they have, such as:

chicken
rice
tomato
garlic

Allow ingredients to be entered one at a time and displayed as removable ingredient chips/tags.

Add a button such as:

"Find Recipes"

Use fetch() to retrieve recipe data from the DummyJSON Recipes API.

Use an endpoint such as:

https://dummyjson.com/recipes?limit=0

so we can retrieve the available recipes and filter them based on the ingredients the user entered.

Do NOT hardcode the recipe results.

==================================================
INGREDIENT MATCHING
==================================================

Normalize ingredient text by:
- converting to lowercase
- trimming whitespace
- handling simple partial matches reasonably

Compare the user's ingredients against each recipe's ingredients.

For each recipe calculate a useful match score, such as:

number of user ingredients found in the recipe /
number of ingredients the user entered

Then show the recipes with the strongest matches first.

Clearly label something like:

"3 of your 4 ingredients match"

or

"75% match"

Do not claim the user has every required ingredient unless that is actually true.

Also show some of the recipe ingredients they would still need.

==================================================
RESULT CARDS
==================================================

Each recipe card should look polished and display useful information from the API, such as:

- recipe image
- recipe name
- cuisine
- difficulty
- prep time
- cook time
- servings
- match percentage
- matched ingredients

When the user clicks a recipe, open a detailed modal or expanded view showing:

- large image
- full ingredient list
- cooking instructions
- prep/cook time
- servings
- cuisine
- difficulty

==================================================
INTERACTIVE FEATURES
==================================================

Add several useful features so this is more than a basic API call:

1. Multiple ingredient input with removable chips.
2. Recipe matching based on the ingredients the user has.
3. Sort options: Best ingredient match; Shortest total time; Highest rating.
4. Filters for cuisine, difficulty, meal type, and maximum cooking/preparation time.
5. Favorites using localStorage, including a saved-recipes-only view.
6. "Surprise Me" picks a random recipe from currently matching results.
7. Clear All button for ingredients and filters.
8. Helpful empty states for empty input, no matches, API failure, and loading.
9. Pressing Enter after typing an ingredient adds the ingredient.
10. Prevent duplicate ingredients.

==================================================
DESIGN / API / README / PORTFOLIO / WORKFLOW
==================================================

Build a polished, accessible, responsive food app without large libraries. Use async/await and fetch(), inspect the real API response first, fetch only once, and comment the request for class explanation. Add the project to the main portfolio as Recipe Finder with a relative `recipe-finder/` Try It link. Create a student-friendly README covering what it does, the API, how the call works, how to run, features, AI tools, and an empty Known Issues section. Do not commit or push anything; report files changed, endpoint and JSON fields, matching, localStorage, local testing, edge cases, security findings, and what to understand before submission.

Is it possible to add nutrition info for the recipe finder as well?
