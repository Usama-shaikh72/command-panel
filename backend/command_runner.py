import asyncio
from pathlib import Path


# Project root
PROJECT_DIR = Path(__file__).resolve().parent.parent


async def run_command(command):
    process = await asyncio.create_subprocess_exec(
        *command,
        cwd=PROJECT_DIR,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    return process