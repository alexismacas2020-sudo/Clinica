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
  const reasonInput = form.querySelector('[name="motivo"]');
  const agendaSteps = [...form.querySelectorAll("[data-agenda-step]")];
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
  const fixedHours = ["08:00", "09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"];
  let availableDates = [];
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

  const updateSteps = () => {
    const step1Complete = Boolean(specialty?.value && doctor?.value && reasonInput?.value.trim());
    const step2Complete = step1Complete && Boolean(dateInput?.value && availableDates.includes(dateInput.value) && !dateInput.validationMessage);
    const step3Complete = step2Complete && Boolean(timeInput?.value);
    const unlocked = [true, step1Complete, step2Complete, step3Complete];
    const completed = [step1Complete, step2Complete, step3Complete, false];
    agendaSteps.forEach((step, index) => {
      step.classList.toggle("is-locked", !unlocked[index]);
      step.classList.toggle("is-complete", completed[index]);
      step.classList.toggle("is-current", unlocked[index] && !completed[index] && !unlocked[index + 1]);
      step.setAttribute("aria-disabled", String(!unlocked[index]));
    });
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
  const hourLabel = (hour) => {
    const value = Number(hour.slice(0, 2));
    const period = value < 12 ? "a. m." : "p. m.";
    const display = value % 12 || 12;
    return `${display}:00 ${period}`;
  };
  const timeButton = (hour, selected, enabled = true) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `time-slot ${enabled ? "is-available" : "is-unavailable"} ${hour === selected ? "active" : ""}`;
    button.textContent = hourLabel(hour);
    button.disabled = !enabled;
    button.setAttribute("aria-disabled", String(!enabled));
    button.addEventListener("click", () => {
      slotsBox.querySelectorAll(".time-slot").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      timeInput.value = hour;
      updateSummary();
      updateSteps();
    });
    return button;
  };
  const renderFixedSlots = (available = [], selected = "", message = "Selecciona una fecha para habilitar las horas disponibles.") => {
    slotsBox.className = "time-slots";
    slotsBox.innerHTML = "";
    [
      { label: "Mañana", icon: "fa-sun", hours: fixedHours.filter((hour) => Number(hour.slice(0, 2)) <= 12) },
      { label: "Tarde", icon: "fa-cloud-sun", hours: fixedHours.filter((hour) => Number(hour.slice(0, 2)) >= 14) },
    ].forEach((group) => {
      const section = document.createElement("section");
      section.className = "time-group";
      section.innerHTML = `<h3><i class="fa-solid ${group.icon}"></i>${group.label}</h3><div class="time-group-buttons"></div>`;
      group.hours.forEach((hour) => section.lastElementChild.appendChild(timeButton(hour, selected, available.includes(hour))));
      slotsBox.appendChild(section);
    });
    const note = document.createElement("p");
    note.className = "time-slots-note";
    note.textContent = message;
    slotsBox.appendChild(note);
  };
  const loadSlots = async (date, selected = "") => {
    dateInput.value = date;
    timeInput.value = "";
    showEmpty(slotsBox, "fa-solid fa-spinner fa-spin", "Consultando horas…");
    const query = new URLSearchParams({ medico: doctor.value, fecha: date, excluir: excluded });
    const data = await (await fetch(`${form.dataset.calendarUrl}?${query}`)).json();
    const available = data.horarios || [];
    renderFixedSlots(available, selected, available.length ? "Selecciona una hora disponible." : "No quedan horas disponibles para este día.");
    if (selected && data.horarios.includes(selected)) timeInput.value = selected;
    updateSummary();
    updateSteps();
  };
  const loadDates = async () => {
    if (!doctor?.value) {
      form.classList.remove("is-calendar-ready");
      availableDates = [];
      dateInput.disabled = true;
      dateInput.value = "";
      renderFixedSlots();
      return;
    }
    dateInput.disabled = true;
    const query = new URLSearchParams({ medico: doctor.value, excluir: excluded });
    const data = await (await fetch(`${form.dataset.calendarUrl}?${query}`)).json();
    availableDates = (data.fechas || []).map((item) => item.fecha);
    dateInput.disabled = false;
    if (!data.fechas?.length) {
      form.classList.remove("is-calendar-ready");
      dateInput.setCustomValidity("Este médico no tiene fechas disponibles.");
      return renderFixedSlots([], "", "Este médico no tiene fechas disponibles.");
    }
    form.classList.add("is-calendar-ready");
    dateInput.min = availableDates[0];
    dateInput.max = availableDates[availableDates.length - 1];
    dateInput.setCustomValidity("");
    if (dateInput.value && availableDates.includes(dateInput.value)) loadSlots(dateInput.value, initialTime);
    else renderFixedSlots();
    updateSteps();
  };
  const loadDoctors = async (reset = true) => {
    if (!specialty?.value) {
      doctor.innerHTML = '<option value="">Selecciona un médico</option>';
      dateInput.value = "";
      timeInput.value = "";
      return loadDates();
    }
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
  reasonInput?.addEventListener("input", updateSteps);
  dateInput?.addEventListener("change", () => {
    timeInput.value = "";
    if (!dateInput.value) {
      dateInput.setCustomValidity("");
      return renderFixedSlots();
    }
    if (!availableDates.includes(dateInput.value)) {
      dateInput.setCustomValidity("La fecha seleccionada no tiene horarios disponibles para este médico.");
      renderFixedSlots([], "", "La fecha seleccionada no tiene horarios disponibles.");
      dateInput.reportValidity();
      updateSummary();
      return updateSteps();
    }
    dateInput.setCustomValidity("");
    loadSlots(dateInput.value);
    updateSteps();
  });
  renderFixedSlots();
  if (!doctor?.value) dateInput.disabled = true;
  updateSteps();
  if (specialty?.value) loadDoctors(false);
  else if (doctor?.value) loadDates();
});
