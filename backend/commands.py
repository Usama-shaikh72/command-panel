COMMANDS = {
    "up": {
        "command": ["make", "up"],
        "description": "Start the Docker stack"
    },
    "down": {
        "command": ["make", "down"],
        "description": "Stop and remove Docker containers"
    },
    "restart": {
        "command": ["make", "restart"],
        "description": "Rebuild and restart Docker stack"
    },
    "reset": {
        "command": ["make", "reset"],
        "description": "Reset containers and database volumes"
    },
    "logs": {
        "command": ["make", "logs"],
        "description": "View Docker logs"
    },
    "test": {
        "command": ["make", "test"],
        "description": "Run pytest"
    },
    "lint": {
        "command": ["make", "lint"],
        "description": "Run Ruff linting"
    },
    "format": {
        "command": ["make", "format"],
        "description": "Format Python files"
    },
    "check": {
        "command": ["make", "check"],
        "description": "Run CI checks"
    },
    "load-test": {
        "command": ["make", "load-test"],
        "description": "Run k6 load test"
    }
}