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
  const password = form.querySelector("[data-credential-password]");
  const photoInput = form.querySelector("[data-photo-input]");
  const photoPreview = form.querySelector("[data-photo-preview]");

  if (password) {
    const wrapper = document.createElement("div");
    wrapper.className = "credential-password-wrap";
    password.parentNode.insertBefore(wrapper, password);
    wrapper.appendChild(password);
    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "credential-password-toggle";
    toggle.setAttribute("aria-label", "Mostrar contraseña");
    toggle.innerHTML = '<i class="fa-regular fa-eye"></i>';
    toggle.addEventListener("click", () => {
      const visible = password.type === "text";
      password.type = visible ? "password" : "text";
      toggle.setAttribute("aria-label", visible ? "Mostrar contraseña" : "Ocultar contraseña");
      toggle.innerHTML = `<i class="fa-regular ${visible ? "fa-eye" : "fa-eye-slash"}"></i>`;
    });
    wrapper.appendChild(toggle);
  }

  photoInput?.addEventListener("change", () => {
    const file = photoInput.files?.[0];
    if (!file || !photoPreview) return;
    const reader = new FileReader();
    reader.addEventListener("load", () => {
      photoPreview.innerHTML = `<img src="${reader.result}" alt="Vista previa de la foto">`;
    });
    reader.readAsDataURL(file);
  });
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
