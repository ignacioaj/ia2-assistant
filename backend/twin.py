from openai import OpenAI
from backend.context import TWIN_INSTRUCTIONS
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gpt-5.4-mini"
MAX_HISTORY_MESSAGES = 20

openai = OpenAI()

def chat(message, history):
    print(history, flush=True)
    history = history[-MAX_HISTORY_MESSAGES:]

    input_messages = [
        {
            "role": msg["role"],
            "content": [
                {
                    "type": "input_text" if msg["role"] == "user" else "output_text",
                    "text": msg["content"]
                }
            ]
        }
        for msg in history
    ]

    input_messages.append(
        {"role": "user", "content": message}
    )

    response = openai.responses.create(
        model=MODEL_NAME,
        instructions=TWIN_INSTRUCTIONS,
        input=input_messages
    )

    response_text = response.output_text

    updated_history = history + [
        {
            "role": "user",
            "content": message
        },
        {
            "role": "assistant",
            "content": response_text
        }
    ]

    return response_text, updated_history