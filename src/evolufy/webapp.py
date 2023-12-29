import gradio as gr
from evolufy import pipeline

predict = pipeline()

with gr.Blocks(title="evolufy") as webapp:
    gr.Markdown("# Greetings from evolufy!")
    inp = gr.Textbox(placeholder="What is your name?")
    out = gr.Textbox()

    inp.change(fn=predict,
               inputs=inp,
               outputs=out)