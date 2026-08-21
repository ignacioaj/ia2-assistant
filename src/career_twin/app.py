from openai import OpenAI

MODEL_NAME = "gpt-5.4-mini"
openai = OpenAI()

system= [{"role":"system", "content": system_prompt}]

def chat(message, history):
    messages = system + history + [{"role":"system", "content": message}]
    response = openai.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools)

    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_calls = message.tool_calls
        results = handle_tool_calls(tool_calls)
        messages.append(message)
        messages.extend(results)
        response = openai.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools)

    return response.choices[0].message.content

if __name__ == "__main__":
