let selectedPasswordCommand = null;

let logsSocket = null;

let logsRunning = false;


// ================================================================
// API
// ================================================================

async function apiRequest(
    url,
    options = {}
) {

    const response = await fetch(
        url,
        {
            ...options,

            headers: {
                "Content-Type": "application/json",

                ...(options.headers || {})
            }
        }
    );


    let data;

    try {

        data = await response.json();

    } catch {

        throw new Error(
            "The server returned an invalid response."
        );

    }


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Request failed."
        );

    }


    return data;
}


// ================================================================
// OUTPUT
// ================================================================

function setOutput(
    text,
    success = true
) {

    const output =
        document.getElementById(
            "output"
        );


    output.textContent =
        text;


    if (success) {

        output.className =
            "min-h-32 overflow-auto rounded-xl border border-slate-800 bg-slate-900 p-5 font-mono text-sm text-slate-300";

    } else {

        output.className =
            "min-h-32 overflow-auto rounded-xl border border-red-500/30 bg-red-500/5 p-5 font-mono text-sm text-red-300";

    }

}


// ================================================================
// EXECUTE COMMAND
// ================================================================

async function executeCommand(
    command
) {

    setOutput(
        `Running make ${command}...`
    );


    try {

        const result =
            await apiRequest(
                `/api/commands/${command}`,
                {
                    method: "POST"
                }
            );


        setOutput(
            result.output ||
            `make ${command} completed.`,
            result.success
        );


        await refreshStatus();

    } catch (error) {

        setOutput(
            error.message,
            false
        );

    }

}


// ================================================================
// PASSWORD COMMANDS
// ================================================================

function openPasswordDialog(
    command
) {

    selectedPasswordCommand =
        command;


    const dialog =
        document.getElementById(
            "password-dialog"
        );


    const title =
        document.getElementById(
            "password-title"
        );


    if (command === "restart") {

        title.textContent =
            "Restart Stack";

    } else {

        title.textContent =
            "Start Stack";

    }


    dialog.classList.remove(
        "hidden"
    );

    dialog.classList.add(
        "flex"
    );


    document
        .getElementById(
            "db-password"
        )
        .focus();

}


function closePasswordDialog() {

    const dialog =
        document.getElementById(
            "password-dialog"
        );


    dialog.classList.add(
        "hidden"
    );

    dialog.classList.remove(
        "flex"
    );


    document
        .getElementById(
            "db-password"
        )
        .value = "";


    selectedPasswordCommand =
        null;

}


async function submitPasswordCommand() {

    const passwordInput =
        document.getElementById(
            "db-password"
        );


    const password =
        passwordInput.value;


    if (!password) {

        alert(
            "Database password cannot be empty."
        );

        return;

    }


    const command =
        selectedPasswordCommand;


    closePasswordDialog();


    setOutput(
        `Running ${command}...`
    );


    try {

        const result =
            await apiRequest(
                `/api/commands/${command}`,
                {
                    method: "POST",

                    body: JSON.stringify({
                        db_password: password
                    })
                }
            );


        /*
         * Make sure the browser no longer
         * keeps the password.
         */

        passwordInput.value = "";


        setOutput(
            result.output ||
            `${command} completed.`,
            result.success
        );


        await refreshStatus();

    } catch (error) {

        passwordInput.value = "";


        setOutput(
            error.message,
            false
        );

    }

}


// ================================================================
// RESET
// ================================================================

function openResetDialog() {

    const dialog =
        document.getElementById(
            "reset-dialog"
        );


    dialog.classList.remove(
        "hidden"
    );

    dialog.classList.add(
        "flex"
    );

}


function closeResetDialog() {

    const dialog =
        document.getElementById(
            "reset-dialog"
        );


    dialog.classList.add(
        "hidden"
    );

    dialog.classList.remove(
        "flex"
    );

}


async function confirmReset() {

    closeResetDialog();


    setOutput(
        "Running make reset..."
    );


    try {

        const result =
            await apiRequest(
                "/api/commands/reset",
                {
                    method: "POST"
                }
            );


        setOutput(
            result.output ||
            "Reset completed.",
            result.success
        );


        await refreshStatus();

    } catch (error) {

        setOutput(
            error.message,
            false
        );

    }

}


// ================================================================
// STATUS
// ================================================================

async function refreshStatus() {

    try {

        const result =
            await apiRequest(
                "/api/status"
            );


        renderServices(
            result.services
        );


    } catch (error) {

        renderServices([]);

    }

}


function renderServices(
    services
) {

    const container =
        document.getElementById(
            "services"
        );


    if (
        !services ||
        services.length === 0
    ) {

        container.innerHTML = `

            <div
                class="rounded-xl border border-slate-800 bg-slate-900 p-5 sm:col-span-2 lg:col-span-4"
            >

                <p class="text-sm text-slate-500">
                    No running Docker Compose services.
                </p>

            </div>

        `;

        return;

    }


    container.innerHTML =
        services
            .map(
                service => {

                    const name =
                        service.Name ||
                        service.Service ||
                        "Unknown";


                    const state =
                        service.State ||
                        service.Status ||
                        "Unknown";


                    const running =
                        state
                            .toLowerCase()
                            .includes(
                                "running"
                            );


                    return `

                        <div
                            class="rounded-xl border border-slate-800 bg-slate-900 p-5"
                        >

                            <div
                                class="flex items-center justify-between"
                            >

                                <h4 class="font-semibold">
                                    ${escapeHtml(name)}
                                </h4>

                                <span
                                    class="h-2.5 w-2.5 rounded-full ${
                                        running
                                            ? "bg-emerald-400"
                                            : "bg-red-400"
                                    }"
                                ></span>

                            </div>


                            <p
                                class="mt-3 text-sm ${
                                    running
                                        ? "text-emerald-400"
                                        : "text-red-400"
                                }"
                            >
                                ${escapeHtml(state)}
                            </p>

                        </div>

                    `;

                }
            )
            .join("");

}


// ================================================================
// LIVE LOGS
// ================================================================

function toggleLogs() {

    if (logsRunning) {

        stopLogs();

    } else {

        startLogs();

    }

}


function startLogs() {

    const logs =
        document.getElementById(
            "logs"
        );


    const button =
        document.getElementById(
            "logs-button"
        );


    logs.textContent =
        "Connecting to Docker logs...\n";


    const protocol =
        window.location.protocol ===
        "https:"
            ? "wss:"
            : "ws:";


    const url =
        `${protocol}//${window.location.host}/ws/logs`;


    logsSocket =
        new WebSocket(url);


    logsSocket.onopen =
        () => {

            logsRunning =
                true;


            button.textContent =
                "Stop Logs";


            button.classList.remove(
                "bg-slate-800"
            );


            button.classList.add(
                "bg-red-600"
            );

        };


    logsSocket.onmessage =
        event => {

            logs.textContent +=
                event.data;


            logs.scrollTop =
                logs.scrollHeight;

        };


    logsSocket.onerror =
        () => {

            logs.textContent +=
                "\n[Control Panel] Log connection error.\n";

        };


    logsSocket.onclose =
        () => {

            logsRunning =
                false;


            button.textContent =
                "Start Logs";


            button.classList.remove(
                "bg-red-600"
            );


            button.classList.add(
                "bg-slate-800"
            );

        };

}


function stopLogs() {

    if (logsSocket) {

        logsSocket.close();

        logsSocket =
            null;

    }


    logsRunning =
        false;

}


// ================================================================
// NAVIGATION
// ================================================================

function showSection(
    section
) {

    const dashboard =
        document.getElementById(
            "dashboard-section"
        );


    const operations =
        document.getElementById(
            "operations-section"
        );


    const logs =
        document.getElementById(
            "logs-section"
        );


    dashboard.classList.add(
        "hidden"
    );

    operations.classList.add(
        "hidden"
    );

    logs.classList.add(
        "hidden"
    );


    if (section === "dashboard") {

        dashboard.classList.remove(
            "hidden"
        );

    }


    if (section === "operations") {

        operations.classList.remove(
            "hidden"
        );

    }


    if (section === "logs") {

        logs.classList.remove(
            "hidden"
        );

    }

}


// ================================================================
// CLEAR OUTPUT
// ================================================================

function clearOutput() {

    document.getElementById(
        "output"
    ).textContent =
        "No command executed.";

}


// ================================================================
// HTML ESCAPING
// ================================================================

function escapeHtml(
    value
) {

    return String(value)
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );

}


// ================================================================
// CONNECTION
// ================================================================

async function checkConnection() {

    const dot =
        document.getElementById(
            "connection-dot"
        );


    const text =
        document.getElementById(
            "connection-text"
        );


    try {

        await apiRequest(
            "/api/health"
        );


        dot.className =
            "h-2.5 w-2.5 rounded-full bg-emerald-400";


        text.textContent =
            "Connected";


        text.className =
            "text-sm text-emerald-400";

    } catch {

        dot.className =
            "h-2.5 w-2.5 rounded-full bg-red-400";


        text.textContent =
            "Disconnected";


        text.className =
            "text-sm text-red-400";

    }

}


// ================================================================
// STARTUP
// ================================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        checkConnection();

        refreshStatus();

        setInterval(
            refreshStatus,
            5000
        );

    }
);