from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from backend.twin import chat


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Remember to change for https://ignacioaj.github.io/
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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