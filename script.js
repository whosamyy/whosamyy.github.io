// AI assistance: Codex drafted this button interaction.
// Toggling a class on body switches the color variables defined in style.css.
const themeButton = document.getElementById("theme-toggle");
themeButton.hidden = false;

themeButton.addEventListener("click", function () {
    const isDark = document.body.classList.toggle("dark-mode");
    themeButton.textContent = isDark ? "Light mode" : "Dark mode";
    themeButton.setAttribute("aria-pressed", String(isDark));
});

// AI assistance: Codex helped add scroll reveals using IntersectionObserver.
// The browser tells us when a section enters the viewport (the visible page).
// Without observer support or with reduced motion, sections stay visible.
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

if ("IntersectionObserver" in window && !reducedMotion.matches) {
    const sectionObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.remove("reveal-pending");
                sectionObserver.unobserve(entry.target); // Animate only once.
            }
        });
    }, { threshold: 0 });

    document.querySelectorAll("main section").forEach(function (section) {
        section.classList.add("reveal-pending");
        sectionObserver.observe(section);

        // Keyboard users should always see the link they are focusing.
        section.addEventListener("focusin", function () {
            section.classList.remove("reveal-pending");
            sectionObserver.unobserve(section);
        });
    });

    reducedMotion.addEventListener("change", function () {
        if (reducedMotion.matches) {
            document.querySelectorAll(".reveal-pending").forEach(function (section) {
                section.classList.remove("reveal-pending");
            });
            sectionObserver.disconnect();
        }
    });
}
