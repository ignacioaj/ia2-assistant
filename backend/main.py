from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from backend.assistant import chat
from backend.pricing import log_usage
from backend.database import save_token_usage


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Remember to change for https://ignacioaj.github.io/
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str

def get_client_ip(request: Request):
    forwarded_for = request.headers.get("X-Forwarded-For")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.client.host

@app.post("/chat")
def chat_endpoint(data: ChatRequest, request: Request):
    history = sessions.get(data.session_id, [])

    response, updated_history, usage = chat(
        data.message,
        history,
    )

    sessions[data.session_id] = updated_history

    ip = get_client_ip(request)

    if usage:

        cost = log_usage(
            model="gpt-5.4-mini",
            usage=usage,
        )

        save_token_usage(
            ip=ip,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            total_tokens=usage.total_tokens,
            cost=cost,
        )

    return {
        "response": response
    }