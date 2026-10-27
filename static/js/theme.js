// Dark/light theme toggle persisted in localStorage (FR-30).
(function () {
  "use strict";
  const STORAGE_KEY = "tablereserve-theme";
  const root = document.documentElement;

  function iconFor(theme) {
    return theme === "dark" ? "bi-sun" : "bi-moon-stars";
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    const icon = document.querySelector("[data-theme-icon]");
    if (icon) {
      icon.classList.remove("bi-sun", "bi-moon-stars");
      icon.classList.add(iconFor(theme));
    }
  }

  // Restore a saved preference, otherwise honour the OS preference.
  const saved = window.localStorage.getItem(STORAGE_KEY);
  if (saved === "dark" || saved === "light") {
    applyTheme(saved);
  } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    applyTheme("dark");
  }

  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(root.getAttribute("data-theme") || "light");
    const toggle = document.getElementById("theme-toggle");
    if (!toggle) {
      return;
    }
    toggle.addEventListener("click", function () {
      const current = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(current);
      window.localStorage.setItem(STORAGE_KEY, current);
    });
  });
})();
