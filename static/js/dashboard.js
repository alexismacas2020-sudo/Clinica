document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const sidebarToggle = document.querySelector("[data-sidebar-toggle]");
  sidebarToggle?.addEventListener("click", () => {
    if (window.innerWidth < 992) body.classList.toggle("sidebar-open");
    else {
      body.classList.toggle("sidebar-collapsed");
      localStorage.setItem("adminSidebarCollapsed", body.classList.contains("sidebar-collapsed") ? "1" : "0");
    }
  });
  if (window.innerWidth >= 992 && localStorage.getItem("adminSidebarCollapsed") === "1") body.classList.add("sidebar-collapsed");
  document.querySelectorAll('.admin-sidebar a[href^="#"]:not(.disabled)').forEach((link) => link.addEventListener("click", () => body.classList.remove("sidebar-open")));

  const credentialPanel = document.querySelector("#crearCredencial");
  if (credentialPanel && window.location.hash === "#crearCredencial" && window.bootstrap?.Collapse) {
    window.bootstrap.Collapse.getOrCreateInstance(credentialPanel, { toggle: false }).show();
    credentialPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  const form = document.querySelector("[data-credential-form]");
  if (!form) return;
  const role = form.querySelector("[data-role-selector]");
  const medicalFields = form.querySelector("[data-medical-fields]");
  const updateFields = () => {
    const isMedical = role?.value === "MEDICO";
    if (medicalFields) medicalFields.hidden = !isMedical;
    medicalFields?.querySelectorAll("input,select").forEach((field) => {
      if (["especialidad", "registro_profesional"].includes(field.name)) field.required = isMedical;
    });
  };
  role?.addEventListener("change", updateFields);
  updateFields();
});
