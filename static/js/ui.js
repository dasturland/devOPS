// General UI behaviours: responsive nav, toast dismissal, floor map and charts.
(function () {
  "use strict";

  // --- Responsive navigation toggle (NFR-04) -----------------------------
  function initNav() {
    const toggle = document.getElementById("nav-toggle");
    const links = document.getElementById("nav-links");
    if (!toggle || !links) {
      return;
    }
    toggle.addEventListener("click", function () {
      const open = links.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // --- Auto-dismiss toast notifications ----------------------------------
  function initToasts() {
    const items = document.querySelectorAll(".toast-item");
    items.forEach(function (item) {
      const close = item.querySelector(".toast-close");
      if (close) {
        close.addEventListener("click", function () {
          item.remove();
        });
      }
      window.setTimeout(function () {
        item.style.opacity = "0";
        window.setTimeout(function () {
          item.remove();
        }, 300);
      }, 5000);
    });
  }

  // --- Interactive floor / table map (FR-11, FR-12) ----------------------
  function initFloorMap() {
    const map = document.querySelector("[data-floor-map]");
    if (!map) {
      return;
    }
    const input = document.querySelector("[data-selected-table]");
    const submitBtn = document.querySelector("[data-select-submit]");
    map.querySelectorAll(".floor-table.is-free").forEach(function (cell) {
      cell.addEventListener("click", function () {
        map.querySelectorAll(".floor-table").forEach(function (c) {
          c.classList.remove("is-selected");
        });
        cell.classList.add("is-selected");
        if (input) {
          input.value = cell.getAttribute("data-table-id") || "";
        }
        if (submitBtn) {
          submitBtn.removeAttribute("disabled");
        }
      });
    });
  }

  // --- Chart.js dashboard charts (FR-22) ---------------------------------
  function initCharts() {
    if (typeof window.Chart === "undefined") {
      return;
    }
    document.querySelectorAll("[data-chart]").forEach(function (canvas) {
      let payload;
      try {
        payload = JSON.parse(canvas.getAttribute("data-chart"));
      } catch (err) {
        return;
      }
      const type = canvas.getAttribute("data-chart-type") || "bar";
      new window.Chart(canvas, {
        type: type,
        data: {
          labels: payload.labels || [],
          datasets: [
            {
              label: canvas.getAttribute("data-chart-label") || "Bronlar",
              data: payload.values || [],
              backgroundColor: [
                "#a9603f", "#c8963e", "#3f7d58", "#4a6d8c", "#b3463b", "#8f4e31"
              ],
              borderWidth: 1
            }
          ]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: type !== "bar" } }
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initNav();
    initToasts();
    initFloorMap();
    initCharts();
  });
})();
