/** @odoo-module **/

const TARGET = "/pydo-it#contacto";

function patchHeaderContactButtons() {
  // 1) Cambia href de cualquier botón del header que vaya a /contactus
  document.querySelectorAll('header a.btn').forEach((a) => {
    const href = a.getAttribute("href") || "";
    const text = (a.innerText || "").trim().toLowerCase();

    // Solo los CTA de "Contáctanos" (por href o por texto)
    if (href.includes("/contactus") || text === "contáctanos" || text === "contactanos") {
      a.setAttribute("href", TARGET);
    }
  });
}

// Corre al cargar y en re-renders del header (sticky/offcanvas)
document.addEventListener("DOMContentLoaded", () => {
  patchHeaderContactButtons();

  const header = document.querySelector("header");
  if (header) {
    new MutationObserver(patchHeaderContactButtons).observe(header, { childList: true, subtree: true });
  }
});

// 2) Y además: aunque lo vuelvan a cambiar, forzamos el click (capturing)
document.addEventListener(
  "click",
  (ev) => {
    const a = ev.target.closest("header a.btn");
    if (!a) return;

    const href = a.getAttribute("href") || "";
    const text = (a.innerText || "").trim().toLowerCase();

    if (href.includes("/contactus") || text === "contáctanos" || text === "contactanos") {
      ev.preventDefault();
      window.location.href = TARGET;
    }
  },
  true
);