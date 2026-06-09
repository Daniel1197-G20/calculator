let display = document.getElementById("display");
let expression = "";

function appendToDisplay(value) {
    if (expression === "0" || expression === "Error") expression = "";
    expression += value;
    display.textContent = expression;
}

function clearDisplay() {
    expression = "";
    display.textContent = "0";
}

function calculate() {
    if (!expression || expression === "Error") return;

    fetch("/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ expression: expression })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("HTTP error " + res.status);
        }
        return res.json();
    })
    .then(data => {
        display.textContent = data.result;
        expression = data.result === "Error" ? "" : data.result;
    })
    .catch(err => {
        console.error("Calculation fetch failed:", err);
        display.textContent = "Error";
        expression = "";
    });
}
