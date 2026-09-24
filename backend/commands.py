from enum import Enum


class Command(str, Enum):
    UP = "up"
    DOWN = "down"
    RESTART = "restart"
    RESET = "reset"
    LOGS = "logs"
    TEST = "test"
    LINT = "lint"
    FORMAT = "format"
    CHECK = "check"
    LOAD_TEST = "load-test"


# Commands exposed to the web control panel.
#
# IMPORTANT:
# The frontend never sends an arbitrary shell command.
# It only sends one of these command names.
COMMANDS: dict[Command, str] = {
    Command.UP: "up",
    Command.DOWN: "down",
    Command.RESTART: "restart",
    Command.RESET: "reset",
    Command.LOGS: "logs",
    Command.TEST: "test",
    Command.LINT: "lint",
    Command.FORMAT: "format",
    Command.CHECK: "check",
    Command.LOAD_TEST: "load-test",
}


def get_command(command: str) -> str:
    """
    Return the Makefile target associated with a command.

    Raises:
        ValueError: if the command isn't allowed.
    """

    try:
        command_enum = Command(command)
    except ValueError as exc:
        raise ValueError(
            f"Unsupported command: {command}"
        ) from exc

    return COMMANDS[command_enum]