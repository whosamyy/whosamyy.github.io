// The separate Flask backend fetches DummyJSON and ranks ingredient matches.
const API_URL = "https://recipe-finder-backend-o6bk.onrender.com/recommend";
const INITIAL_MESSAGE = "Add ingredients, then choose Find recipes to see your best matches.";
let activeRequest = null;
const state = { recipes: [], ingredients: [], favorites: loadFavorites(), searched: false, resultIngredients: [] };
const $ = (selector) => document.querySelector(selector);
const el = {
  input: $("#ingredient-input"), chips: $("#ingredient-chips"), message: $("#input-message"),
  grid: $("#recipe-grid"), status: $("#status"), count: $("#result-count"), modal: $("#recipe-modal"), modalContent: $("#modal-content"),
  sort: $("#sort"), cuisine: $("#cuisine"), difficulty: $("#difficulty"), mealType: $("#meal-type"), maxTime: $("#max-time"), favoritesOnly: $("#favorites-only"), surprise: $("#surprise-me")
};

function loadFavorites() { try { const saved = JSON.parse(localStorage.getItem("recipe-finder-favorites")); return Array.isArray(saved) ? saved.filter(Number.isFinite) : []; } catch { return []; } }
function saveFavorites() { try { localStorage.setItem("recipe-finder-favorites", JSON.stringify(state.favorites)); } catch { el.message.textContent = "Your favorite is saved for this visit, but browser storage is unavailable."; } }
function normalized(text) { return String(text).toLowerCase().replace(/[^a-z0-9 ]/g, " ").trim(); }
function escapeHtml(value) { const div = document.createElement("div"); div.textContent = value; return div.innerHTML.replace(/"/g, "&quot;").replace(/'/g, "&#39;"); }

function validRecipe(recipe) {
  if (!recipe || typeof recipe !== "object") return false;
  return ["name", "image", "cuisine", "difficulty"].every(key => typeof recipe[key] === "string") &&
    ["ingredients", "instructions", "mealType", "matchedIngredients", "missingIngredients"].every(key =>
      Array.isArray(recipe[key]) && recipe[key].every(value => typeof value === "string")) &&
    ["id", "prepTimeMinutes", "cookTimeMinutes", "rating", "servings", "caloriesPerServing", "reviewCount", "matchCount", "matchPercentage"].every(key =>
      Number.isFinite(recipe[key]) && recipe[key] >= 0);
}
function cancelRequest() {
  if (activeRequest) activeRequest.abort();
  activeRequest = null;
  el.grid.setAttribute("aria-busy", "false");
  $("#find-recipes").disabled = false;
}
function invalidateResults() {
  cancelRequest();
  state.searched = false; state.recipes = []; state.resultIngredients = [];
  el.grid.innerHTML = ""; el.count.textContent = ""; el.surprise.disabled = true;
  el.status.textContent = INITIAL_MESSAGE;
}
async function fetchRecipes() {
  cancelRequest();
  const controller = new AbortController();
  activeRequest = controller;
  const ingredients = [...state.ingredients];
  state.searched = false; state.recipes = [];
  el.grid.innerHTML = ""; el.count.textContent = ""; el.surprise.disabled = true;
  el.grid.setAttribute("aria-busy", "true");
  $("#find-recipes").disabled = true;
  el.status.textContent = "Finding recipes... The server may take a few seconds to wake up.";
  // Allow a sleeping Render service up to two minutes to respond.
  const timeout = setTimeout(() => controller.abort(), 120000);
  try {
    const response = await fetch(API_URL, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ingredients, limit: 100 }), signal: controller.signal
    });
    let data;
    try { data = await response.json(); }
    catch { throw new Error(response.ok ? "The server returned unreadable recipe data. Please try again." : `The recipe server is unavailable (HTTP ${response.status}). Please try again shortly.`); }
    if (!response.ok || data?.error || data?.success === false) {
      throw new Error(typeof data?.error === "string" ? `Couldn't find recipes: ${data.error}` : `The recipe server could not complete your request (HTTP ${response.status}). Please try again.`);
    }
    if (!data || data.success !== true || !Array.isArray(data.recipes) || !data.recipes.every(validRecipe) ||
        !Array.isArray(data.ingredients) || !data.ingredients.length || !data.ingredients.every(value => typeof value === "string")) {
      throw new Error("The server returned incomplete recipe data. Please try again shortly.");
    }
    if (activeRequest !== controller) return;
    state.recipes = data.recipes; state.resultIngredients = data.ingredients; state.searched = true;
    populateFilters(); renderResults();
  } catch (error) {
    if (activeRequest !== controller) return;
    el.status.textContent = controller.signal.aborted
      ? "The server is taking longer than expected to wake up. Please choose Find recipes to try again."
      : error instanceof TypeError ? "Couldn't reach the recipe server. Check your connection and try again shortly."
      : error.message;
  } finally {
    clearTimeout(timeout);
    if (activeRequest === controller) { activeRequest = null; el.grid.setAttribute("aria-busy", "false"); $("#find-recipes").disabled = false; }
  }
}
function populateFilters() {
  addOptions(el.cuisine, [...new Set(state.recipes.map(r => r.cuisine))].sort());
  addOptions(el.difficulty, [...new Set(state.recipes.map(r => r.difficulty))].sort());
  addOptions(el.mealType, [...new Set(state.recipes.flatMap(r => r.mealType || []))].sort());
}
function addOptions(select, values) { const selected = select.value; select.length = 1; if (selected && !values.includes(selected)) values.push(selected); values.forEach(value => select.insertAdjacentHTML("beforeend", `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`)); select.value = selected; }

function addIngredient() {
  const ingredients = el.input.value.split(",").map(value => value.trim().replace(/\s+/g, " ")).filter(Boolean);
  if (!ingredients.length) { el.message.textContent = "Type an ingredient first."; return false; }
  if (ingredients.some(value => value.length > 100 || !/[\p{L}\p{N}]/u.test(value))) { el.message.textContent = "Use ingredient names of at most 100 characters, containing a letter or number."; return false; }
  const added = ingredients.filter((value, index) => !state.ingredients.some(item => normalized(item) === normalized(value)) && ingredients.findIndex(item => normalized(item) === normalized(value)) === index);
  if (state.ingredients.length + added.length > 50) { el.message.textContent = "Please use at most 50 ingredients."; return false; }
  if (!added.length) { el.message.textContent = "Those ingredients are already on your list."; el.input.value = ""; return true; }
  state.ingredients.push(...added); el.input.value = ""; el.message.textContent = ""; invalidateResults(); renderChips(); return true;
}

function renderChips() {
  el.chips.innerHTML = state.ingredients.map((ingredient, index) => `<span class="chip">${escapeHtml(ingredient)} <button type="button" data-remove="${index}" aria-label="Remove ${escapeHtml(ingredient)}">×</button></span>`).join("");
  el.chips.querySelectorAll("[data-remove]").forEach(button => button.addEventListener("click", () => { state.ingredients.splice(Number(button.dataset.remove), 1); invalidateResults(); renderChips(); }));
}
function currentResults() {
  let results = state.recipes.map(recipe => ({ recipe, matched: recipe.matchedIngredients, score: recipe.matchPercentage / 100 }));
  if (el.cuisine.value) results = results.filter(item => item.recipe.cuisine === el.cuisine.value);
  if (el.difficulty.value) results = results.filter(item => item.recipe.difficulty === el.difficulty.value);
  if (el.mealType.value) results = results.filter(item => (item.recipe.mealType || []).includes(el.mealType.value));
  if (el.maxTime.value) results = results.filter(item => item.recipe.prepTimeMinutes + item.recipe.cookTimeMinutes <= Number(el.maxTime.value));
  if (el.favoritesOnly.checked) results = results.filter(item => state.favorites.includes(item.recipe.id));
  const sort = el.sort.value;
  return results.sort((a, b) => sort === "time" ? totalTime(a.recipe) - totalTime(b.recipe) : sort === "rating" ? b.recipe.rating - a.recipe.rating : 0);
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
  const saved = state.favorites.includes(recipe.id), needed = recipe.missingIngredients.slice(0, 3);
  return `<article class="recipe-card"><img class="recipe-image" src="${escapeHtml(recipe.image)}" alt="${escapeHtml(recipe.name)}" loading="lazy"><div class="card-body"><div class="card-top"><h3>${escapeHtml(recipe.name)}</h3><button class="heart" data-favorite="${recipe.id}" aria-label="${saved ? "Remove" : "Save"} ${escapeHtml(recipe.name)}">${saved ? "♥" : "♡"}</button></div><p class="meta">${escapeHtml(recipe.cuisine)} · ${escapeHtml(recipe.difficulty)} · ★ ${recipe.rating}<br>Prep ${recipe.prepTimeMinutes} min · Cook ${recipe.cookTimeMinutes} min · Serves ${recipe.servings}</p><p class="nutrition">⚡ ${recipe.caloriesPerServing} calories per serving</p><span class="match">${recipe.matchCount} of ${state.resultIngredients.length} ingredients match (${Math.round(score * 100)}%)</span><p class="matched"><strong>You have:</strong> ${escapeHtml(matched.join(", "))}<br><strong>Still need:</strong> ${escapeHtml(needed.join(", ") || "nothing listed")}</p><button class="details-button" data-details="${recipe.id}" type="button">View recipe</button></div></article>`;
}
function toggleFavorite(id) { state.favorites = state.favorites.includes(id) ? state.favorites.filter(item => item !== id) : [...state.favorites, id]; saveFavorites(); renderResults(); }
function openDetails(id) {
  const recipe = state.recipes.find(item => item.id === id); if (!recipe) return;
  el.modalContent.innerHTML = `<img class="modal-image" src="${escapeHtml(recipe.image)}" alt="${escapeHtml(recipe.name)}"><div class="modal-body"><h2 id="modal-title">${escapeHtml(recipe.name)}</h2><p class="meta">${escapeHtml(recipe.cuisine)} · ${escapeHtml(recipe.difficulty)} · ★ ${recipe.rating} (${recipe.reviewCount} reviews)</p><div class="detail-grid"><div><strong>Prep</strong>${recipe.prepTimeMinutes} min</div><div><strong>Cook</strong>${recipe.cookTimeMinutes} min</div><div><strong>Serves</strong>${recipe.servings}</div><div><strong>Meal</strong>${escapeHtml((recipe.mealType || []).join(", "))}</div></div><section class="nutrition-panel" aria-label="Nutrition information"><p class="eyebrow">NUTRITION</p><p><strong>${recipe.caloriesPerServing} calories</strong> per serving</p><small>Nutrition values are provided by DummyJSON and are shown for general information.</small></section><h3>Ingredients</h3><ul>${recipe.ingredients.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul><h3>Instructions</h3><ol>${recipe.instructions.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ol></div>`;
  el.modal.showModal();
}
function findRecipes() { if (el.input.value.trim() && !addIngredient()) return; if (!state.ingredients.length) { el.message.textContent = "Add at least one ingredient so I can look for matches."; return; } el.message.textContent = ""; return fetchRecipes(); }
function clearAll() { invalidateResults(); state.ingredients = []; state.searched = false; el.input.value = ""; el.message.textContent = ""; document.querySelectorAll(".controls select").forEach(select => select.selectedIndex = 0); el.favoritesOnly.checked = false; renderChips(); el.grid.innerHTML = ""; el.count.textContent = ""; el.status.textContent = INITIAL_MESSAGE; el.surprise.disabled = true; }

$("#add-ingredient").addEventListener("click", addIngredient); el.input.addEventListener("keydown", event => { if (event.key === "Enter") { event.preventDefault(); addIngredient(); } }); $("#find-recipes").addEventListener("click", findRecipes); $("#clear-all").addEventListener("click", clearAll); el.surprise.addEventListener("click", () => { const results = currentResults(); if (results.length) openDetails(results[Math.floor(Math.random() * results.length)].recipe.id); }); $("#close-modal").addEventListener("click", () => el.modal.close()); document.querySelectorAll(".controls select, #favorites-only").forEach(control => control.addEventListener("change", renderResults));
el.status.textContent = INITIAL_MESSAGE;
