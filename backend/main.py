import os

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.assistant import chat
from backend.pricing import log_usage
from backend.database.token_usage import save_token_usage, is_usage_blocked
from backend.database.sessions import save_session

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Remember to change for https://ignacioaj.github.io/
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = os.getenv("MODEL_NAME")
MAXIMUM_DAILY_COST_PER_USER = os.getenv("MAXIMUM_DAILY_COST_PER_USER")
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

    ip = get_client_ip(request)

    if is_usage_blocked(ip):
        raise HTTPException(
            status_code=429,
            detail="Daily usage limit reached. Please try again later.",
        )

    history = sessions.get(data.session_id, [])

    response, updated_history, usage = chat(
        data.message,
        history,
    )

    sessions[data.session_id] = updated_history

    cost = 0

    if usage:

        cost = log_usage(
            model=MODEL_NAME,
            usage=usage,
        )

        save_token_usage(
            ip=ip,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            total_tokens=usage.total_tokens,
            cost=cost,
        )

    save_session(
        session_id=data.session_id,
        ip=ip,
        question=data.message,
        answer=response,
        status="success",
        cost=cost
    )

    return {
        "response": response
    }