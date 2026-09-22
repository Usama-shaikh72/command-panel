from fastapi import FastAPI
from backend.commands import COMMANDS
app = FastAPI()


@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Command Panel Backend is running"
    }

@app.get("/commands")
def get_commands():
    return COMMANDS