import os

from openai import OpenAI
from dotenv import load_dotenv

from backend.context import TWIN_INSTRUCTIONS
from backend.tools import tools, handle_tool_calls

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME")
MAXIMUM_DAILY_COST_PER_USER = os.getenv("MAXIMUM_DAILY_COST_PER_USER")
MAX_HISTORY_MESSAGES = 20
PROMPT_CACHE_KEY = "career-twin-v1"

openai = OpenAI()


def chat(message, history):
    history = history[-MAX_HISTORY_MESSAGES:]

    input_messages = [
        {
            "role": msg["role"],
            "content": [
                {
                    "type": "input_text"
                    if msg["role"] == "user"
                    else "output_text",
                    "text": msg["content"],
                }
            ],
        }
        for msg in history
    ]

    input_messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    response = openai.responses.create(
        model=MODEL_NAME,
        instructions=TWIN_INSTRUCTIONS,
        input=input_messages,
        tools=tools,
        prompt_cache_key=PROMPT_CACHE_KEY,
    )

    while any(item.type == "function_call" for item in response.output):
        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        tool_results = handle_tool_calls(tool_calls)

        input_messages.extend(response.output)
        input_messages.extend(tool_results)

        response = openai.responses.create(
            model=MODEL_NAME,
            instructions=TWIN_INSTRUCTIONS,
            input=input_messages,
            tools=tools,
            prompt_cache_key=PROMPT_CACHE_KEY,
        )

    response_text = response.output_text

    updated_history = history + [
        {
            "role": "user",
            "content": message,
        },
        {
            "role": "assistant",
            "content": response_text,
        },
    ]

    return response_text, updated_history, response.usage