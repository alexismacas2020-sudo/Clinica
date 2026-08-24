document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-toast]").forEach((toast, index) => {
    const close = () => {
      toast.classList.add("is-leaving");
      window.setTimeout(() => toast.remove(), 240);
    };
    toast.style.setProperty("--toast-delay", `${index * 90}ms`);
    toast.querySelector("[data-toast-close]")?.addEventListener("click", close);
    const timeout = window.setTimeout(close, 5200 + index * 350);
    toast.addEventListener("mouseenter", () => window.clearTimeout(timeout), { once: true });
  });

  document.querySelectorAll("form[novalidate]").forEach((form) => {
    const fields = form.querySelectorAll("input, select, textarea");
    fields.forEach((field) => {
      const validate = () => {
        field.classList.toggle("is-valid", field.checkValidity() && Boolean(field.value));
        field.classList.toggle("is-invalid", !field.checkValidity());
        field.setAttribute("aria-invalid", String(!field.checkValidity()));
      };
      field.addEventListener("blur", validate);
      field.addEventListener("input", () => field.classList.remove("is-invalid"));
    });
    form.addEventListener("submit", () => {
      if (!form.checkValidity()) fields.forEach((field) => field.dispatchEvent(new Event("blur")));
    });
  });
});
