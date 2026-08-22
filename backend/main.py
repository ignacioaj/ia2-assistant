from fastapi import FastAPI
from pydantic import BaseModel

from backend.twin import chat


app = FastAPI()

sessions = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.post("/chat")
def chat_endpoint(data: ChatRequest):
    history = sessions.get(data.session_id, [])

    response, updated_history = chat(data.message, history)

    sessions[data.session_id] = updated_history

    return {
        "response": response
    }