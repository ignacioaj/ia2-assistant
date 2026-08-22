from openai import OpenAI
from assistant.context import TWIN_INSTRUCTIONS
# from assistant.tools import tools, handle_tool_calls
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gpt-5.4-mini"
MAX_HISTORY_MESSAGES = 20

openai = OpenAI()


# system = [{"role": "system", "content": TWIN_INSTRUCTIONS}]

def chat(message, history):
    print(history, flush=True)
    history = history[-MAX_HISTORY_MESSAGES:]

    input_messages = [
        {
            "role": msg["role"],
            "content": [
                {
                    "type": "input_text" if msg["role"] == "user" else "output_text",
                    "text": msg["content"][0]["text"]
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

    # while response.choices[0].finish_reason == "tool_calls":
    #     message = response.choices[0].message
    #     tool_calls = message.tool_callsF
    #     results = handle_tool_calls(tool_calls)
    #     messages.append(message)
    #     messages.extend(results)
    #     response = openai.chat.completions.create(
    #         model=MODEL_NAME,
    #         messages=messages,
    #         tools=tools
    #     )

    return response.output_text


demo = gr.ChatInterface(
    fn=chat,
    title="IA² — Ignacio's Career Twin",
    description="Ask me anything about Ignacio's professional background.",
)

if __name__ == "__main__":
    demo.launch()