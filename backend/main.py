import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.command_runner import (
    run_make_command,
    run_restart,
    run_reset,
    stream_logs,
)


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FRONTEND_DIR = PROJECT_ROOT / "frontend"


# -------------------------------------------------------------------
# FastAPI
# -------------------------------------------------------------------

app = FastAPI(
    title="FastAPI Observability Command Panel",
    description="Browser control panel for the observability stack",
    version="1.0.0",
)


# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Frontend
# -------------------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)


@app.get(
    "/",
    include_in_schema=False,
)
async def frontend():
    return FileResponse(
        FRONTEND_DIR / "index.html",
    )


# -------------------------------------------------------------------
# Request models
# -------------------------------------------------------------------

class PasswordRequest(BaseModel):
    db_password: str = Field(
        min_length=1,
        description="Database password",
    )


class CommandResponse(BaseModel):
    command: str
    success: bool
    exit_code: int
    output: str


# -------------------------------------------------------------------
# Health
# -------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "command-panel",
    }


# -------------------------------------------------------------------
# Docker status
# -------------------------------------------------------------------

@app.get("/api/status")
async def status():
    """
    Get the current Docker Compose service status.

    We use docker compose directly here because status is
    information rather than an operation.
    """

    process = await asyncio.create_subprocess_exec(
        "docker",
        "compose",
        "ps",
        "--format",
        "json",
        cwd=PROJECT_ROOT,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    stdout, _ = await process.communicate()

    output = stdout.decode(
        "utf-8",
        errors="replace",
    )

    services = []

    for line in output.splitlines():

        if not line.strip():
            continue

        try:
            services.append(
                json.loads(line)
            )

        except json.JSONDecodeError:
            services.append(
                {
                    "raw": line,
                }
            )

    return {
        "success": process.returncode == 0,
        "services": services,
        "raw": output,
    }


# -------------------------------------------------------------------
# Start
# -------------------------------------------------------------------

@app.post(
    "/api/commands/up",
    response_model=CommandResponse,
)
async def start_stack(
    request: PasswordRequest,
):
    """
    Start the Docker stack.

    The password is passed to `make up` through DB_PASS.
    It is NOT placed in the command-line arguments.
    """

    exit_code, output = await run_make_command(
        "up",
        db_password=request.db_password,
    )

    return CommandResponse(
        command="up",
        success=exit_code == 0,
        exit_code=exit_code,
        output=output,
    )


# -------------------------------------------------------------------
# Down
# -------------------------------------------------------------------

@app.post(
    "/api/commands/down",
    response_model=CommandResponse,
)
async def stop_stack():

    exit_code, output = await run_make_command(
        "down",
    )

    return CommandResponse(
        command="down",
        success=exit_code == 0,
        exit_code=exit_code,
        output=output,
    )


# -------------------------------------------------------------------
# Restart
# -------------------------------------------------------------------

@app.post(
    "/api/commands/restart",
    response_model=CommandResponse,
)
async def restart_stack(
    request: PasswordRequest,
):

    exit_code, output = await run_restart(
        request.db_password,
    )

    return CommandResponse(
        command="restart",
        success=exit_code == 0,
        exit_code=exit_code,
        output=output,
    )


# -------------------------------------------------------------------
# Reset
# -------------------------------------------------------------------

@app.post(
    "/api/commands/reset",
    response_model=CommandResponse,
)
async def reset_stack():

    exit_code, output = await run_reset()

    return CommandResponse(
        command="reset",
        success=exit_code == 0,
        exit_code=exit_code,
        output=output,
    )


# -------------------------------------------------------------------
# Development commands
# -------------------------------------------------------------------

ALLOWED_COMMANDS = {
    "test",
    "lint",
    "format",
    "check",
    "load-test",
}


@app.post(
    "/api/commands/{command}",
    response_model=CommandResponse,
)
async def execute_command(
    command: str,
):

    if command not in ALLOWED_COMMANDS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown command: {command}",
        )

    exit_code, output = await run_make_command(
        command,
    )

    return CommandResponse(
        command=command,
        success=exit_code == 0,
        exit_code=exit_code,
        output=output,
    )


# -------------------------------------------------------------------
# Live logs
# -------------------------------------------------------------------

@app.websocket("/ws/logs")
async def logs(
    websocket: WebSocket,
):

    await websocket.accept()

    try:

        async for line in stream_logs():

            await websocket.send_text(
                line
            )

    except Exception as exc:

        try:
            await websocket.send_text(
                f"\n[Command Panel] "
                f"Log stream error: {exc}\n"
            )
        except Exception:
            pass

    finally:

        try:
            await websocket.close()
        except Exception:
            pass