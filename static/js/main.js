document.addEventListener("DOMContentLoaded", () => {
  const backToTop = document.querySelector("[data-back-to-top]");

  if (backToTop) {
    const updateVisibility = () => backToTop.classList.toggle("is-visible", window.scrollY > 500);
    updateVisibility();
    window.addEventListener("scroll", updateVisibility, { passive: true });
    backToTop.addEventListener("click", () => {
      const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      window.scrollTo({ top: 0, behavior: reducedMotion ? "auto" : "smooth" });
    });
  }

  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", () => {
      const button = form.querySelector('button[type="submit"][data-loading-text]');
      if (!button || !form.checkValidity()) return;
      button.dataset.originalText = button.innerHTML;
      button.innerHTML = `<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> ${button.dataset.loadingText}`;
      button.disabled = true;
      button.setAttribute("aria-busy", "true");
    });
  });
});
