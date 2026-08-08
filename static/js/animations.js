document.addEventListener("DOMContentLoaded", () => {
  const elements = document.querySelectorAll("[data-animate]");
  if (!elements.length) return;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  elements.forEach((element) => {
    const delay = Number.parseInt(element.dataset.animateDelay || "0", 10);
    const duration = Number.parseInt(element.dataset.animateDuration || "600", 10);
    element.style.setProperty("--animate-delay", `${Math.max(0, delay)}ms`);
    element.style.setProperty("--animate-duration", `${Math.max(100, duration)}ms`);
  });

  if (reduceMotion || !("IntersectionObserver" in window)) {
    elements.forEach((element) => element.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      observer.unobserve(entry.target);
    });
  }, { rootMargin: "0px 0px -8%", threshold: 0.12 });

  elements.forEach((element) => observer.observe(element));
});
