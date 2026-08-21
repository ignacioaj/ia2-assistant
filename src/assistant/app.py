from openai import OpenAI
from assistant.context import TWIN_SYSTEM_PROMPT
from assistant.tools import tools, handle_tool_calls
import gradio as gr

MODEL_NAME = "gpt-5.4-mini"
MAX_HISTORY_MESSAGES = 20

openai = OpenAI()

system= [{"role":"system", "content": TWIN_SYSTEM_PROMPT}]

def chat(message, history):
    # * Uncomment lines when tools are used *
    # messages = system + history + [{"role":"user", "content": message}]
    history = history[-MAX_HISTORY_MESSAGES:]
    input_messages= history + [{"role":"user", "content": message}]
    response = openai.responses.create(model=MODEL_NAME, instructions=TWIN_SYSTEM_PROMPT,input=input_messages)

    # while response.choices[0].finish_reason == "tool_calls":
    #     message = response.choices[0].message
    #     tool_calls = message.tool_calls
    #     results = handle_tool_calls(tool_calls)
    #     messages.append(message)
    #     messages.extend(results)
    #     response = openai.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools)

    return response.choices[0].message.content

demo = gr.ChatInterface(
    fn=chat,
    title="Career Twin",
    description="Ask me anything about my professional background.",
)

if __name__ == "__main__":
    demo.launch()
