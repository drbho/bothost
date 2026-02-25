const leadForm = document.getElementById("lead-form");
const result = document.getElementById("form-result");

if (leadForm && result) {
  leadForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(leadForm);
    const name = data.get("nome");

    result.textContent = `Grazie ${name}! Ti contatteremo entro 24 ore lavorative.`;
    leadForm.reset();
  });
}
