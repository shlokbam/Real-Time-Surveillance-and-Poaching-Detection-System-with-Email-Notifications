import gradio as gr
from app import app

def launch_flask():
    return "WildGuard AI is running. Use the interface below."

with gr.Blocks() as demo:
    gr.Markdown("# 🛡️ WildGuard AI – Poaching Detection System")
    gr.Markdown("Upload a video to run AI-based surveillance and poaching detection.")
    gr.Markdown("👉 Click **Open App** below to launch the dashboard.")

    btn = gr.Button("Open WildGuard Dashboard")
    output = gr.Textbox()

    btn.click(fn=launch_flask, outputs=output)

demo.launch(server_name="0.0.0.0", server_port=7860)
