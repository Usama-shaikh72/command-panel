const terminal = document.getElementById("terminal");
const clearButton = document.getElementById("clearTerminal");


// Get all command buttons
const commandButtons = document.querySelectorAll(".command-btn");


// Add click event to every command button
commandButtons.forEach((button) => {

    button.addEventListener("click", () => {

        const command = button.dataset.command;

        addTerminalLine(`$ make ${command}`, "text-blue-400");

        addTerminalLine(
            `Waiting to execute make ${command}...`,
            "text-slate-500"
        );

    });

});


// Add text to terminal
function addTerminalLine(text, colorClass = "text-slate-300") {

    const line = document.createElement("div");

    line.className = colorClass;

    line.textContent = text;

    terminal.appendChild(line);

    terminal.scrollTop = terminal.scrollHeight;
}


// Clear terminal
clearButton.addEventListener("click", () => {

    terminal.innerHTML = "";

    addTerminalLine(
        "$ Terminal cleared",
        "text-slate-500"
    );

});