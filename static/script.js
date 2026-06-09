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
