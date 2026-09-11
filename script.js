// AI assistance: Codex drafted this button interaction.
// Toggling a class on body switches the color variables defined in style.css.
const themeButton = document.getElementById("theme-toggle");
themeButton.hidden = false;

themeButton.addEventListener("click", function () {
    const isDark = document.body.classList.toggle("dark-mode");
    themeButton.textContent = isDark ? "Light mode" : "Dark mode";
    themeButton.setAttribute("aria-pressed", String(isDark));
});
