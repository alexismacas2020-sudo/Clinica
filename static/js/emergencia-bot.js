document.addEventListener("DOMContentLoaded", () => {
  const bot = document.querySelector("[data-emergency-bot]");
  const greeting = document.querySelector(".emergency-bot__greeting");
  document.querySelector("[data-emergency-greeting-close]")?.addEventListener("click", () => greeting?.remove());
  bot?.addEventListener("toggle", () => {
    if (bot.open) greeting?.classList.add("is-hidden");
  });
});
