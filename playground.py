import gradio as gr

from backend.assistant import chat


def playground_chat(message, history):
    formatted_history = [
        {
            "role": msg["role"],
            "content": msg["content"][0]["text"],
        }
        for msg in history
    ]

    response, _ = chat(message, formatted_history)

    return response


demo = gr.ChatInterface(
    fn=playground_chat,
    title="Career Twin Playground",
)

demo.launch()

if __name__ == "__main__":
    demo.launch()