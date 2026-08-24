document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-calendar-form]");
  if (!form) return;
  const specialty = form.querySelector('[name="especialidad"]');
  const doctor = form.querySelector('[name="medico"]');
  const dateInput = form.querySelector('[name="fecha"]');
  const timeInput = form.querySelector('[name="hora"]');
  const datesBox = form.querySelector("[data-calendar-dates]");
  const slotsBox = form.querySelector("[data-time-slots]");
  const submit = form.querySelector('.agenda-submit [type="submit"]');
  const termsCheckbox = form.querySelector("[data-terms-checkbox]");
  const termsError = form.querySelector("[data-terms-error]");
  const acceptTermsButton = document.querySelector("[data-accept-terms]");
  const summary = document.createElement("div");
  summary.className = "appointment-selection";
  summary.hidden = true;
  summary.innerHTML = '<i class="fa-solid fa-calendar-check"></i><div><small>Selección de la cita</small><strong data-selection-text></strong></div>';
  form.querySelector(".agenda-submit")?.before(summary);
  const initialDoctor = doctor?.value || "";
  const initialDate = dateInput?.value || "";
  const initialTime = timeInput?.value?.slice(0, 5) || "";
  const excluded = form.dataset.citaId || "";
  const paymentMethod = form.querySelector('[name="metodo_pago"]');
  const transferPayment = form.querySelector("[data-transfer-payment]");
  const toggleTransferPayment = () => {
    if (!transferPayment || !paymentMethod) return;
    const isTransfer = paymentMethod.value === "TRANSFERENCIA";
    transferPayment.hidden = !isTransfer;
    transferPayment.setAttribute("aria-hidden", String(!isTransfer));
    if (!isTransfer) {
      const bank = form.querySelector('[name="banco"]');
      const receipt = form.querySelector('[name="comprobante_pago"]');
      if (bank) bank.value = "";
      if (receipt) receipt.value = "";
    }
  };
  paymentMethod?.addEventListener("change", toggleTransferPayment);
  toggleTransferPayment();

  const updateSummary = () => {
    const complete = Boolean(doctor?.value && dateInput?.value && timeInput?.value);
    const termsAccepted = !termsCheckbox || termsCheckbox.checked;
    summary.hidden = !complete;
    if (complete) {
      const parsed = new Date(`${dateInput.value}T12:00:00`);
      const label = new Intl.DateTimeFormat("es", { weekday: "long", day: "numeric", month: "long" }).format(parsed);
      summary.querySelector("[data-selection-text]").textContent = `${doctor.selectedOptions[0].text} · ${label} · ${timeInput.value.slice(0, 5)}`;
    }
    if (submit) {
      submit.disabled = !(complete && termsAccepted && form.classList.contains("is-calendar-ready"));
      submit.setAttribute("aria-disabled", String(submit.disabled));
    }
  };

  const updateTerms = () => {
    const accepted = Boolean(termsCheckbox?.checked);
    if (termsError) termsError.hidden = accepted;
    termsCheckbox?.closest(".booking-terms")?.classList.toggle("is-accepted", accepted);
    updateSummary();
  };

  termsCheckbox?.addEventListener("change", updateTerms);
  acceptTermsButton?.addEventListener("click", () => {
    termsCheckbox.checked = true;
    updateTerms();
  });
  form.addEventListener("submit", (event) => {
    if (termsCheckbox && !termsCheckbox.checked) {
      event.preventDefault();
      if (termsError) termsError.hidden = false;
      termsCheckbox.closest(".booking-terms")?.classList.add("has-error");
      termsCheckbox.focus();
    }
  });
  updateTerms();
  const showEmpty = (box, icon, message) => {
    box.className = box === datesBox ? "availability-placeholder" : "time-slots";
    box.innerHTML = icon ? `<i class="${icon}"></i><p>${message}</p>` : `<p>${message}</p>`;
    updateSummary();
  };
  const timeButton = (hour, selected) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `time-slot ${hour === selected ? "active" : ""}`;
    button.textContent = hour;
    button.addEventListener("click", () => {
      slotsBox.querySelectorAll(".time-slot").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      timeInput.value = hour;
      updateSummary();
    });
    return button;
  };
  const loadSlots = async (date, selected = "") => {
    dateInput.value = date;
    timeInput.value = "";
    showEmpty(slotsBox, "fa-solid fa-spinner fa-spin", "Consultando horas…");
    const query = new URLSearchParams({ medico: doctor.value, fecha: date, excluir: excluded });
    const data = await (await fetch(`${form.dataset.calendarUrl}?${query}`)).json();
    slotsBox.className = "time-slots";
    if (!data.horarios?.length) return showEmpty(slotsBox, "", "No quedan horas disponibles para este día.");
    slotsBox.innerHTML = "";
    [
      { label: "Mañana", icon: "fa-sun", hours: data.horarios.filter((hour) => Number(hour.slice(0, 2)) < 12) },
      { label: "Tarde", icon: "fa-cloud-sun", hours: data.horarios.filter((hour) => Number(hour.slice(0, 2)) >= 12) },
    ].filter((group) => group.hours.length).forEach((group) => {
      const section = document.createElement("section");
      section.className = "time-group";
      section.innerHTML = `<h3><i class="fa-solid ${group.icon}"></i>${group.label}</h3><div class="time-group-buttons"></div>`;
      group.hours.forEach((hour) => section.lastElementChild.appendChild(timeButton(hour, selected)));
      slotsBox.appendChild(section);
    });
    if (selected && data.horarios.includes(selected)) timeInput.value = selected;
    updateSummary();
  };
  const loadDates = async () => {
    if (!doctor?.value) {
      form.classList.remove("is-calendar-ready");
      return showEmpty(datesBox, "fa-regular fa-calendar", "Selecciona un médico para consultar su calendario.");
    }
    showEmpty(datesBox, "fa-solid fa-spinner fa-spin", "Consultando disponibilidad…");
    const query = new URLSearchParams({ medico: doctor.value, excluir: excluded });
    const data = await (await fetch(`${form.dataset.calendarUrl}?${query}`)).json();
    datesBox.className = "calendar-days";
    datesBox.innerHTML = "";
    if (!data.fechas?.length) {
      form.classList.remove("is-calendar-ready");
      return showEmpty(datesBox, "fa-regular fa-calendar-xmark", "Este médico no tiene fechas disponibles.");
    }
    form.classList.add("is-calendar-ready");
    data.fechas.forEach((item) => {
      const parsed = new Date(`${item.fecha}T12:00:00`);
      const button = document.createElement("button");
      button.type = "button";
      button.className = `calendar-day ${item.fecha === dateInput.value ? "active" : ""}`;
      button.innerHTML = `<strong>${new Intl.DateTimeFormat("es", { weekday: "short", day: "numeric", month: "short" }).format(parsed)}</strong><small>${item.cupos} horarios disponibles</small>`;
      button.addEventListener("click", () => {
        datesBox.querySelectorAll(".calendar-day").forEach((day) => day.classList.remove("active"));
        button.classList.add("active");
        loadSlots(item.fecha);
      });
      datesBox.appendChild(button);
    });
    if (dateInput.value && data.fechas.some((item) => item.fecha === dateInput.value)) loadSlots(dateInput.value, initialTime);
    else showEmpty(slotsBox, "", "Selecciona una fecha para ver sus horas.");
  };
  const loadDoctors = async (reset = true) => {
    if (!specialty?.value) return;
    const selected = reset ? "" : initialDoctor;
    const data = await (await fetch(`${form.dataset.doctorsUrl}?especialidad=${encodeURIComponent(specialty.value)}`)).json();
    doctor.innerHTML = '<option value="">Selecciona un médico</option>';
    data.medicos.forEach((item) => doctor.add(new Option(`${item.nombre} · ${item.especialidad}`, item.id, false, String(item.id) === String(selected))));
    dateInput.value = reset ? "" : initialDate;
    timeInput.value = reset ? "" : initialTime;
    loadDates();
  };
  specialty?.addEventListener("change", () => loadDoctors(true));
  doctor?.addEventListener("change", () => { dateInput.value = ""; timeInput.value = ""; loadDates(); });
  if (specialty?.value) loadDoctors(false);
  else if (doctor?.value) loadDates();
});
