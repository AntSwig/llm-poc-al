import pickle
import gradio as gr
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import PromptLayerChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)


system_template = """
You are an AI assistant for burpsuite.
You are given the following extracted parts of a long document and a question. Provide an answer in the form of a bcheck script.
Use the following pieces of context to answer the question:

{summaries}

If you don't know the answer, just say that you don't know, don't try to make up an answer.
ALWAYS return a "Sources" part in your answer.
The "Sources" part should be a reference to the source of the document from which you got your answer.

Example of your response should be:

```
metadata:
    language: v1-beta
    name: "Request-level collaborator based"
    description: "Blind SSRF with out-of-band detection"
    author: "Carlos Montoya"

given request then
    send request:
        headers:
            "Referer": {{generate_collaborator_address()}}

    if http interactions then
        report issue:
            severity: high
            confidence: firm
            detail: "This site fetches arbitrary URLs specified in the Referer header."
            remediation: "Ensure that the site does not directly request URLs from the Referer header."
    end if

Sources:
1. abc
2. xyz
```

"""
messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}"),
]
prompt = ChatPromptTemplate.from_messages(messages)


def get_chain(store):
    chain_type_kwargs = {"prompt": prompt}
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        PromptLayerChatOpenAI(temperature=0),
        chain_type="stuff",
        retriever=store.as_retriever(),
        chain_type_kwargs=chain_type_kwargs,
        reduce_k_below_max_tokens=True,
    )
    return chain


with open("faiss_store.pkl", "rb") as f:
    store = pickle.load(f)

chain = get_chain(store)

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
        response = chain({"question": user_message, "history": history})
        # Append user message and response to chat history
        history.append((user_message, response["answer"]))
        return gr.update(value=""), history

    message.submit(respond, [message, chatbot], [message, chatbot], queue=False)
    submit.click(respond, [message, chatbot], [message, chatbot], queue=False)
    clear.click(lambda: None, None, chatbot, queue=False)

    demo.launch(share=True, server_name=("0.0.0.0"))
