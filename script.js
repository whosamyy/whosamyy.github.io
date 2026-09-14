// AI assistance: Codex drafted this button interaction.
// Toggling a class on body switches the color variables defined in style.css.
const themeButton = document.getElementById("theme-toggle");
themeButton.hidden = false;

themeButton.addEventListener("click", function () {
    const isDark = document.body.classList.toggle("dark-mode");
    themeButton.textContent = isDark ? "Light mode" : "Dark mode";
    themeButton.setAttribute("aria-pressed", String(isDark));
});

// AI assistance: Codex helped add repeatable scroll reveals and a typing intro.
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const sections = document.querySelectorAll("main section");
const intro = document.querySelector(".intro");
const introText = intro.querySelector(".intro-full").textContent;
const typedText = intro.querySelector(".intro-typed");
let sectionObserver;
let typingTimer;

function startAnimations() {
    sectionObserver?.disconnect();
    clearTimeout(typingTimer);
    sections.forEach(function (section) {
        section.classList.remove("reveal-active");
    });
    intro.classList.remove("is-typing");
    typedText.textContent = "";

    // Keep the full sentence immediately readable when reduced motion is enabled.
    if (reducedMotion.matches) return;

    intro.classList.add("is-typing");
    let characterIndex = 0;
    function typeNextCharacter() {
        characterIndex += 1;
        typedText.textContent = introText.slice(0, characterIndex);
        if (characterIndex < introText.length) {
            typingTimer = setTimeout(typeNextCharacter,
                introText[characterIndex - 1] === "," ? 220 : 55);
        } else {
            typingTimer = setTimeout(function () {
                intro.classList.remove("is-typing");
            }, 650);
        }
    }
    typingTimer = setTimeout(typeNextCharacter, 350);

    if ("IntersectionObserver" in window) {
        sectionObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                entry.target.classList.toggle("reveal-active", entry.isIntersecting);
            });
        }, { threshold: 0 });
        sections.forEach(function (section) {
            sectionObserver.observe(section);
        });
    }
}

startAnimations();
// Back/forward navigation can restore a page without running its scripts again.
window.addEventListener("pageshow", function (event) {
    if (event.persisted) startAnimations();
});
reducedMotion.addEventListener("change", startAnimations);

// A small, fixed set of petals; CSS handles the motion and reduced-motion setting.
const sakuraBackground = document.querySelector(".sakura-background");
for (let i = 0; i < 18; i += 1) {
    const petal = document.createElement("span");
    petal.className = "sakura-petal";
    petal.style.setProperty("--left", `${Math.random() * 100}%`);
    petal.style.setProperty("--size", `${8 + Math.random() * 7}px`);
    petal.style.setProperty("--duration", `${14 + Math.random() * 12}s`);
    // Negative delays fill the screen gently as soon as the page loads.
    petal.style.setProperty("--delay", `${-Math.random() * 26}s`);
    sakuraBackground.appendChild(petal);
}
