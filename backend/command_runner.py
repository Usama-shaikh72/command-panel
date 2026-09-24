import asyncio
import os
from collections.abc import AsyncIterator
from pathlib import Path

from backend.commands import get_command


# Project root:
#
# fastapi-observability/
# ├── backend/
# │   └── command_runner.py
# ├── frontend/
# └── Makefile
#
PROJECT_ROOT = Path(__file__).resolve().parent.parent


async def run_make_command(
    command: str,
    *,
    db_password: str | None = None,
) -> tuple[int, str]:
    """
    Run an approved Makefile target.

    Returns:
        (exit_code, combined_stdout_stderr)
    """

    make_target = get_command(command)

    environment = os.environ.copy()

    # make up already supports DB_PASS:
    #
    # PASS="$(DB_PASS)"
    #
    # so we can securely provide the password through
    # the environment instead of passing it as a CLI argument.
    if db_password is not None:
        environment["DB_PASS"] = db_password

    process = await asyncio.create_subprocess_exec(
        "make",
        make_target,
        cwd=PROJECT_ROOT,
        env=environment,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    stdout, _ = await process.communicate()

    output = stdout.decode(
        "utf-8",
        errors="replace",
    )

    return process.returncode or 0, output


async def run_restart(
    db_password: str,
) -> tuple[int, str]:
    """
    Restart the stack.

    The current Makefile's restart target doesn't request DB_PASS,
    so the safest web-panel behavior is:

        make down
        DB_PASS=<password> make up
    """

    down_code, down_output = await run_make_command(
        "down",
    )

    if down_code != 0:
        return (
            down_code,
            down_output,
        )

    up_code, up_output = await run_make_command(
        "up",
        db_password=db_password,
    )

    return (
        up_code,
        down_output + "\n" + up_output,
    )


async def run_reset() -> tuple[int, str]:
    """
    Run the reset command.

    This uses the Makefile's reset target.
    """

    return await run_make_command(
        "reset",
    )


async def stream_logs() -> AsyncIterator[str]:
    """
    Stream `make logs` output.

    This stays alive until the client disconnects
    or the process exits.
    """

    make_target = get_command("logs")

    process = await asyncio.create_subprocess_exec(
        "make",
        make_target,
        cwd=PROJECT_ROOT,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    if process.stdout is None:
        return

    try:
        while True:
            line = await process.stdout.readline()

            if not line:
                break

            yield line.decode(
                "utf-8",
                errors="replace",
            )

    finally:
        if process.returncode is None:
            process.terminate()

            try:
                await asyncio.wait_for(
                    process.wait(),
                    timeout=2,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()