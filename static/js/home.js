document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll("[data-counter]");
  if (!counters.length) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const formatNumber = (number) => new Intl.NumberFormat("es-ES").format(number);

  const animateCounter = (counter) => {
    const target = Number.parseInt(counter.dataset.counter || "0", 10);
    if (reducedMotion) {
      counter.textContent = formatNumber(target);
      return;
    }
    const startTime = performance.now();
    const duration = 1200;
    const update = (now) => {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      counter.textContent = formatNumber(Math.round(target * eased));
      if (progress < 1) window.requestAnimationFrame(update);
    };
    window.requestAnimationFrame(update);
  };

  if (!("IntersectionObserver" in window)) {
    counters.forEach(animateCounter);
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      animateCounter(entry.target);
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.6 });
  counters.forEach((counter) => observer.observe(counter));
});
