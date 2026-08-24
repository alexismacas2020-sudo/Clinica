document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-consultation-form]");
  if (!form) return;
  const tabs = form.querySelectorAll("[data-tab-target]");
  const panels = form.querySelectorAll("[data-tab-panel]");
  tabs.forEach((tab) => tab.addEventListener("click", () => {
    tabs.forEach((item) => item.classList.remove("active"));
    panels.forEach((item) => item.classList.remove("active"));
    tab.classList.add("active");
    form.querySelector(`[data-tab-panel="${tab.dataset.tabTarget}"]`)?.classList.add("active");
  }));

  const panelConError = [...panels].find((panel) => panel.querySelector(".invalid-feedback, .is-invalid"));
  if (panelConError) {
    form.querySelector(`[data-tab-target="${panelConError.dataset.tabPanel}"]`)?.click();
  }
});
