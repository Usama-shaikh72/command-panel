# ⚡ Command Panel

A web-based control panel for managing and monitoring an observability/Docker stack through a simple browser interface.

The project uses **FastAPI** for the backend and **Tailwind CSS + JavaScript** for the frontend. The long-term goal is to provide a safe web interface for running predefined project commands and displaying their output in a terminal-style UI.

---

## 🚀 Project Overview

The Command Panel is designed to provide a browser-based interface for commands currently available in the project's `Makefile`.

Instead of manually running commands such as:

```bash
make up
make down
make restart
make test
make logs
```

the user will eventually be able to click buttons in the web application and see the command output directly in the browser.

### Planned Architecture

```text
┌──────────────────────────────┐
│        Web Browser           │
│                              │
│   Tailwind CSS + JavaScript  │
└──────────────┬───────────────┘
               │
               │ WebSocket
               ▼
┌──────────────────────────────┐
│         FastAPI              │
│         Backend              │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Safe Command Runner     │
│                              │
│      Allowed commands only   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│          Makefile            │
│                              │
│ Docker / pytest / Ruff / k6  │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     Docker Observability     │
│          Stack               │
└──────────────────────────────┘
```

---

# 📁 Current Project Structure

```text
command-panel/
│
├── backend/
│   ├── main.py
│   ├── commands.py
│   └── command_runner.py
│
├── frontend/
│   ├── index.html
│   └── app.js
│
├── venv/
│
└── requirements.txt
```

---

# 🛠️ Technologies

### Backend

* Python
* FastAPI
* Uvicorn
* WebSockets — planned
* Async subprocess execution — started

### Frontend

* HTML
* JavaScript
* Tailwind CSS
* Browser WebSocket API — planned

### DevOps / Project Tools

* Docker
* Docker Compose
* Make
* Bash
* pytest
* Ruff
* Grafana k6

---

# ✅ Current Progress

## 1. Project Created

The initial project structure was created:

```text
command-panel/
├── backend/
├── frontend/
├── venv/
└── requirements.txt
```

A Python virtual environment was created for the backend.

---

## 2. Python Dependencies

`requirements.txt` currently contains:

```text
fastapi
uvicorn[standard]
```

Dependencies were installed successfully.

---

# 3. FastAPI Backend

The initial FastAPI application was created in:

```text
backend/main.py
```

Current functionality includes:

```text
GET /
```

which returns:

```json
{
    "status": "online",
    "message": "Command Panel Backend is running"
}
```

The backend can be started using:

```bash
uvicorn backend.main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

---

# 4. Command Registry

A safe command registry was created in:

```text
backend/commands.py
```

The application currently recognizes these commands:

| Command     | Purpose                               |
| ----------- | ------------------------------------- |
| `up`        | Start Docker stack                    |
| `down`      | Stop Docker containers                |
| `restart`   | Rebuild and restart stack             |
| `reset`     | Reset containers and database volumes |
| `logs`      | View Docker logs                      |
| `test`      | Run pytest                            |
| `lint`      | Run Ruff linting                      |
| `format`    | Format Python files                   |
| `check`     | Run CI-style checks                   |
| `load-test` | Run k6 load test                      |

The commands are stored as predefined argument lists rather than accepting arbitrary shell commands.

Example:

```python
"up": {
    "command": ["make", "up"],
    "description": "Start the Docker stack"
}
```

This approach is important because the eventual web application should **not allow arbitrary shell commands from the browser**.

---

# 5. Commands API

The backend exposes:

```text
GET /commands
```

This returns the available command registry.

Example:

```text
http://127.0.0.1:8000/commands
```

The endpoint allows the frontend to know which predefined commands are available.

---

# 6. Command Runner

A basic asynchronous command runner was created:

```text
backend/command_runner.py
```

It uses Python's asynchronous subprocess functionality:

```python
asyncio.create_subprocess_exec()
```

The project root is automatically detected:

```python
PROJECT_DIR = Path(__file__).resolve().parent.parent
```

The runner is designed to eventually:

```text
FastAPI
   ↓
Command Registry
   ↓
Command Runner
   ↓
Make command
   ↓
stdout/stderr
   ↓
WebSocket
   ↓
Browser terminal
```

The actual command execution has **not been connected to the browser yet**.

---

# 7. Frontend

The frontend was created in:

```text
frontend/index.html
```

The UI currently contains:

### Docker Stack

* 🚀 UP
* 🛑 DOWN
* 🔄 RESTART
* 🧹 RESET

### Development

* 🧪 TEST
* 🔍 LINT
* ✨ FORMAT
* ✅ CHECK

### Other

* 📋 LOGS
* 🔥 LOAD TEST

---

# 8. Terminal UI

The frontend contains a terminal-style output area.

It currently displays messages such as:

```text
$ Command Center initialized

Select a command above to get started.
```

When a command button is clicked, it currently displays:

```text
$ make test
Waiting to execute make test...
```

At this stage, these are only frontend messages.

The commands are **not actually being executed yet**.

---

# 9. Frontend JavaScript

The frontend logic is currently in:

```text
frontend/app.js
```

It handles:

* Finding command buttons
* Reading the `data-command` attribute
* Displaying the selected command
* Adding output to the terminal
* Clearing the terminal

Example:

```html
<button data-command="test">
    🧪
    <span>TEST</span>
</button>
```

JavaScript reads:

```javascript
const command = button.dataset.command;
```

and displays:

```text
$ make test
```

---

# 10. Running the Frontend

The frontend can be served using Python's built-in HTTP server.

From the project:

```bash
cd frontend
python -m http.server 5500
```

Then open:

```text
http://127.0.0.1:5500
```

---

# ⚠️ Current Environment Issue

The project's Makefile uses:

```make
SHELL := /bin/bash
```

and commands such as:

```bash
make up
make down
docker compose up
pytest
ruff
k6
```

The current Windows environment does not have:

```text
make
bash
```

We tested:

```powershell
make --version
```

and received:

```text
make : The term 'make' is not recognized...
```

We also tested:

```powershell
bash --version
```

and received:

```text
bash : The term 'bash' is not recognized...
```

WSL was also checked:

```powershell
wsl --status
```

and Windows reported that WSL is not currently installed.

Therefore, **actual Makefile command execution has not been enabled yet**.

---

# 🐧 Next Environment Step

The next step is to set up a Linux environment using:

```text
WSL2 + Ubuntu
```

This will provide:

```text
Bash
Make
Linux environment
Docker integration
```

which matches the environment expected by the existing Makefile.

We should verify:

```bash
make --version
```

and:

```bash
bash --version
```

before implementing actual command execution.

---

# 🔜 Next Development Steps

## Phase 1 — Environment

* [ ] Install/configure WSL2
* [ ] Install Ubuntu
* [ ] Verify Bash
* [ ] Verify Make
* [ ] Verify Docker access
* [ ] Verify Docker Compose
* [ ] Verify pytest
* [ ] Verify Ruff
* [ ] Verify k6

---

## Phase 2 — Backend Command Execution

Connect:

```text
Frontend
   ↓
FastAPI
   ↓
Command Registry
   ↓
Command Runner
   ↓
Makefile
```

The backend should return:

* Command started
* Live output
* Errors
* Exit code
* Completion status

---

## Phase 3 — WebSockets

Implement:

```text
Browser
   │
   │ WebSocket
   ▼
FastAPI
   │
   ▼
Command Process
```

This will allow output to appear in the browser in real time.

For example:

```text
$ make test

Running tests...

test_api.py ........
test_database.py ....
test_auth.py ........

==============================
12 passed
==============================

Process exited with code 0
```

---

# 🔐 Security Requirements

The final application should **not** expose a general-purpose terminal.

The backend should only allow predefined commands.

For example:

```text
Allowed:

make up
make down
make restart
make test
```

but not:

```text
rm -rf /
curl malicious-site
arbitrary shell commands
```

Additional security features planned:

* Command allowlist
* Authentication
* Authorization
* Command timeout
* Process cancellation
* Working-directory restriction
* Resource limits
* Confirmation for destructive commands
* Protection for database passwords
* Secure WebSocket handling

---

# ⚠️ High-Impact Commands

Some Makefile commands require additional protection.

### `make reset`

This command removes containers and database volumes.

It should eventually require confirmation:

```text
Are you sure?

This will delete database volumes.

[Cancel] [Confirm Reset]
```

### `make load-test`

This generates traffic against the system.

It should also require explicit confirmation.

### `make up`

The current Makefile can request a database password interactively.

The eventual web interface needs a secure way to provide this password without displaying or logging it.

---

# 🎯 Final Goal

The completed application should look approximately like:

```text
┌─────────────────────────────────────────────────────┐
│ ⚡ Command Center                     ● Backend     │
│    Observability Stack Control Panel                │
│                                                     │
│ Docker Stack                                        │
│                                                     │
│ [ 🚀 UP ] [ 🛑 DOWN ] [ 🔄 RESTART ] [ 🧹 RESET ] │
│                                                     │
│ Development                                         │
│                                                     │
│ [ 🧪 TEST ] [ 🔍 LINT ] [ ✨ FORMAT ] [ ✅ CHECK ] │
│                                                     │
│ Other                                               │
│                                                     │
│ [ 📋 LOGS ] [ 🔥 LOAD TEST ]                       │
│                                                     │
│ Terminal                              [Clear]       │
│ ┌─────────────────────────────────────────────────┐ │
│ │ $ make test                                     │ │
│ │                                                 │ │
│ │ Running tests...                                │ │
│ │ test_api.py ........                            │ │
│ │ test_database.py ....                           │ │
│ │                                                 │ │
│ │ 12 passed                                       │ │
│ │                                                 │ │
│ │ Process exited with code 0                      │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

# 📌 Current Status

**Overall:** 🟡 In Development

### Completed

* [x] Project setup
* [x] Python virtual environment
* [x] FastAPI setup
* [x] Uvicorn setup
* [x] Frontend UI
* [x] Tailwind CSS integration
* [x] Command buttons
* [x] Terminal UI
* [x] Command registry
* [x] `/commands` API
* [x] Basic asynchronous command runner

### In Progress

* [ ] Linux/WSL environment
* [ ] Actual command execution
* [ ] WebSocket connection
* [ ] Live command output
* [ ] Process management
* [ ] Error handling
* [ ] Security
* [ ] Authentication
* [ ] Production deployment

---

## 👨‍💻 Development Note

The project is intentionally being built step-by-step.

The current priority is to establish a reliable development environment first, then connect the frontend to the backend and finally implement safe real-time command execution.
