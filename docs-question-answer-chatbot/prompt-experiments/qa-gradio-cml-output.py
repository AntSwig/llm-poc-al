import argparse
import os
import pickle

import gradio as gr
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)

system_template = """Use the following pieces of context to answer the users question.
If you don't know the answer, just say "Hmm..., I'm not sure.", don't try to make up an answer.
ALWAYS return a "Sources" part in your answer.
The "Sources" part should be a reference to the source of the document from which you got your answer.

Example of your response should be:

```
The answer is foo

Sources:
1. abc
2. xyz
```
Begin!
----------------
{summaries}
"""
messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}"),
]
prompt = ChatPromptTemplate.from_messages(messages)


def get_chain(store):
    chain_type_kwargs = {"prompt": prompt}
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        ChatOpenAI(temperature=0),
        chain_type="stuff",
        retriever=store.as_retriever(),
        chain_type_kwargs=chain_type_kwargs,
        reduce_k_below_max_tokens=True,
    )
    return chain


parser = argparse.ArgumentParser(description="Portswigger docs Q&A")
parser.add_argument("question", type=str, help="Your question for Portswigger")
args = parser.parse_args()

with open("faiss_store.pkl", "rb") as f:
    store = pickle.load(f)

chain = get_chain(store)
result = chain({"question": args.question})

print(f"Answer: {result['answer']}")

# Front end web app

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## Portswigger docs Q&A")
    with gr.Column():
        chatbot = gr.Chatbot()
        with gr.Row():
            with gr.Column():
                message = gr.Textbox(
                    label="Chat Message Box",
                    placeholder="Chat Message Box",
                    show_label=False,
                )
            with gr.Column():
                with gr.Row():
                    submit = gr.Button("Submit")
                    clear = gr.Button("Clear")
                    chat_history = []

    def respond(user_message, history):
        # Get response from QA chain
        response = chain({"question": user_message, "chat_history": history})
        # Append user message and response to chat history
        history.append((user_message, response["answer"]))
        return gr.update(value=""), history

    message.submit(respond, [message, chatbot], [message, chatbot], queue=False)
    clear.click(lambda: None, None, chatbot, queue=False)

    demo.launch(share=False)
