import gradio as gr
from backend.assistant import chat

demo = gr.ChatInterface(
    fn=chat,
    title="IA² — Ignacio's Career Twin",
    description="Ask me anything about Ignacio's professional background.",
)

if __name__ == "__main__":
    demo.launch()