// Recipe Finder uses DummyJSON's public, keyless recipes endpoint.
// fetch() sends an HTTP GET request; response.json() turns the JSON response
// into JavaScript objects. We use recipes plus fields including ingredients,
// image, cuisine, difficulty, mealType, prepTimeMinutes, cookTimeMinutes, and rating.
const API_URL = "https://dummyjson.com/recipes?limit=0";
const state = { recipes: [], ingredients: [], favorites: loadFavorites(), searched: false };
const $ = (selector) => document.querySelector(selector);
const el = {
  input: $("#ingredient-input"), chips: $("#ingredient-chips"), message: $("#input-message"),
  grid: $("#recipe-grid"), status: $("#status"), count: $("#result-count"), modal: $("#recipe-modal"), modalContent: $("#modal-content"),
  sort: $("#sort"), cuisine: $("#cuisine"), difficulty: $("#difficulty"), mealType: $("#meal-type"), maxTime: $("#max-time"), favoritesOnly: $("#favorites-only"), surprise: $("#surprise-me")
};

function loadFavorites() { try { return JSON.parse(localStorage.getItem("recipe-finder-favorites")) || []; } catch { return []; } }
function saveFavorites() { localStorage.setItem("recipe-finder-favorites", JSON.stringify(state.favorites)); }
function normalized(text) { return String(text).toLowerCase().replace(/[^a-z0-9 ]/g, " ").trim(); }
function matchesIngredient(userIngredient, recipeIngredient) {
  const user = normalized(userIngredient), recipe = normalized(recipeIngredient);
  if (!user || !recipe) return false;
  const userWords = user.split(/\s+/), recipeWords = recipe.split(/\s+/);
  return recipe.includes(user) || user.includes(recipe) || userWords.some(word => word.length > 2 && recipeWords.some(part => part === word || part.startsWith(word) || word.startsWith(part)));
}
function getMatch(recipe) {
  const matched = state.ingredients.filter(ingredient => recipe.ingredients.some(item => matchesIngredient(ingredient, item)));
  return { recipe, matched, score: state.ingredients.length ? matched.length / state.ingredients.length : 0 };
}
function escapeHtml(value) { const div = document.createElement("div"); div.textContent = value; return div.innerHTML; }

async function fetchRecipes() {
  try {
    const response = await fetch(API_URL);
    if (!response.ok) throw new Error(`The API returned ${response.status}.`);
    const data = await response.json();
    if (!data || !Array.isArray(data.recipes)) throw new Error("The recipe data was not in the expected format.");
    state.recipes = data.recipes;
    populateFilters();
    el.status.textContent = "Add ingredients, then choose Find recipes to see your best matches.";
  } catch (error) {
    el.status.textContent = `Couldn't load recipes right now. Check your connection and try reloading. (${error.message})`;
  }
}
function populateFilters() {
  addOptions(el.cuisine, [...new Set(state.recipes.map(r => r.cuisine))].sort());
  addOptions(el.difficulty, [...new Set(state.recipes.map(r => r.difficulty))].sort());
  addOptions(el.mealType, [...new Set(state.recipes.flatMap(r => r.mealType || []))].sort());
}
function addOptions(select, values) { values.forEach(value => select.insertAdjacentHTML("beforeend", `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`)); }

function addIngredient() {
  const ingredient = el.input.value.trim().replace(/\s+/g, " ");
  if (!ingredient) { el.message.textContent = "Type an ingredient first."; return; }
  if (state.ingredients.some(item => normalized(item) === normalized(ingredient))) { el.message.textContent = "That ingredient is already on your list."; return; }
  state.ingredients.push(ingredient); el.input.value = ""; el.message.textContent = ""; renderChips();
}
function renderChips() {
  el.chips.innerHTML = state.ingredients.map((ingredient, index) => `<span class="chip">${escapeHtml(ingredient)} <button type="button" data-remove="${index}" aria-label="Remove ${escapeHtml(ingredient)}">×</button></span>`).join("");
  el.chips.querySelectorAll("[data-remove]").forEach(button => button.addEventListener("click", () => { state.ingredients.splice(Number(button.dataset.remove), 1); renderChips(); if (state.searched) renderResults(); }));
}
function currentResults() {
  let results = state.recipes.map(getMatch).filter(item => item.score > 0);
  if (el.cuisine.value) results = results.filter(item => item.recipe.cuisine === el.cuisine.value);
  if (el.difficulty.value) results = results.filter(item => item.recipe.difficulty === el.difficulty.value);
  if (el.mealType.value) results = results.filter(item => (item.recipe.mealType || []).includes(el.mealType.value));
  if (el.maxTime.value) results = results.filter(item => item.recipe.prepTimeMinutes + item.recipe.cookTimeMinutes <= Number(el.maxTime.value));
  if (el.favoritesOnly.checked) results = results.filter(item => state.favorites.includes(item.recipe.id));
  const sort = el.sort.value;
  return results.sort((a, b) => sort === "time" ? totalTime(a.recipe) - totalTime(b.recipe) : sort === "rating" ? b.recipe.rating - a.recipe.rating : b.score - a.score || b.recipe.rating - a.recipe.rating);
}
function totalTime(recipe) { return recipe.prepTimeMinutes + recipe.cookTimeMinutes; }
function renderResults() {
  if (!state.searched) return;
  const results = currentResults(); el.surprise.disabled = !results.length;
  el.count.textContent = results.length ? `${results.length} recipe${results.length === 1 ? "" : "s"} found` : "";
  if (!results.length) { el.grid.innerHTML = `<div class="empty"><h3>No recipes match these choices yet.</h3><p>Try fewer ingredients, remove a filter, or check your spelling.</p></div>`; el.status.textContent = ""; return; }
  el.status.textContent = "";
  el.grid.innerHTML = results.map(item => card(item)).join("");
  el.grid.querySelectorAll("[data-favorite]").forEach(button => button.addEventListener("click", () => toggleFavorite(Number(button.dataset.favorite))));
  el.grid.querySelectorAll("[data-details]").forEach(button => button.addEventListener("click", () => openDetails(Number(button.dataset.details))));
}
function card({ recipe, matched, score }) {
  const saved = state.favorites.includes(recipe.id), needed = recipe.ingredients.filter(item => !matched.some(ingredient => matchesIngredient(ingredient, item))).slice(0, 3);
  return `<article class="recipe-card"><img class="recipe-image" src="${escapeHtml(recipe.image)}" alt="${escapeHtml(recipe.name)}" loading="lazy"><div class="card-body"><div class="card-top"><h3>${escapeHtml(recipe.name)}</h3><button class="heart" data-favorite="${recipe.id}" aria-label="${saved ? "Remove" : "Save"} ${escapeHtml(recipe.name)}">${saved ? "♥" : "♡"}</button></div><p class="meta">${escapeHtml(recipe.cuisine)} · ${escapeHtml(recipe.difficulty)} · ★ ${recipe.rating}<br>Prep ${recipe.prepTimeMinutes} min · Cook ${recipe.cookTimeMinutes} min · Serves ${recipe.servings}</p><p class="nutrition">⚡ ${recipe.caloriesPerServing} calories per serving</p><span class="match">${matched.length} of ${state.ingredients.length} ingredients match (${Math.round(score * 100)}%)</span><p class="matched"><strong>You have:</strong> ${escapeHtml(matched.join(", "))}<br><strong>Still need:</strong> ${escapeHtml(needed.join(", ") || "nothing listed")}</p><button class="details-button" data-details="${recipe.id}" type="button">View recipe</button></div></article>`;
}
function toggleFavorite(id) { state.favorites = state.favorites.includes(id) ? state.favorites.filter(item => item !== id) : [...state.favorites, id]; saveFavorites(); renderResults(); }
function openDetails(id) {
  const recipe = state.recipes.find(item => item.id === id); if (!recipe) return;
  el.modalContent.innerHTML = `<img class="modal-image" src="${escapeHtml(recipe.image)}" alt="${escapeHtml(recipe.name)}"><div class="modal-body"><h2 id="modal-title">${escapeHtml(recipe.name)}</h2><p class="meta">${escapeHtml(recipe.cuisine)} · ${escapeHtml(recipe.difficulty)} · ★ ${recipe.rating} (${recipe.reviewCount} reviews)</p><div class="detail-grid"><div><strong>Prep</strong>${recipe.prepTimeMinutes} min</div><div><strong>Cook</strong>${recipe.cookTimeMinutes} min</div><div><strong>Serves</strong>${recipe.servings}</div><div><strong>Meal</strong>${escapeHtml((recipe.mealType || []).join(", "))}</div></div><section class="nutrition-panel" aria-label="Nutrition information"><p class="eyebrow">NUTRITION</p><p><strong>${recipe.caloriesPerServing} calories</strong> per serving</p><small>Nutrition values are provided by DummyJSON and are shown for general information.</small></section><h3>Ingredients</h3><ul>${recipe.ingredients.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul><h3>Instructions</h3><ol>${recipe.instructions.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ol></div>`;
  el.modal.showModal();
}
function findRecipes() { if (!state.ingredients.length) { el.message.textContent = "Add at least one ingredient so I can look for matches."; return; } state.searched = true; el.message.textContent = ""; renderResults(); }
function clearAll() { state.ingredients = []; state.searched = false; el.input.value = ""; el.message.textContent = ""; document.querySelectorAll(".controls select").forEach(select => select.selectedIndex = 0); el.favoritesOnly.checked = false; renderChips(); el.grid.innerHTML = ""; el.count.textContent = ""; el.status.textContent = state.recipes.length ? "Add ingredients, then choose Find recipes to see your best matches." : ""; el.surprise.disabled = true; }

$("#add-ingredient").addEventListener("click", addIngredient); el.input.addEventListener("keydown", event => { if (event.key === "Enter") { event.preventDefault(); addIngredient(); } }); $("#find-recipes").addEventListener("click", findRecipes); $("#clear-all").addEventListener("click", clearAll); el.surprise.addEventListener("click", () => { const results = currentResults(); if (results.length) openDetails(results[Math.floor(Math.random() * results.length)].recipe.id); }); $("#close-modal").addEventListener("click", () => el.modal.close()); document.querySelectorAll(".controls select, #favorites-only").forEach(control => control.addEventListener("change", renderResults));
fetchRecipes();
