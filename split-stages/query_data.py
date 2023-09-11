import pickle
import gradio as gr

from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import PromptLayerChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)

user_question: str = "What is a sql injection"


def get_chain(store, prompt):
    chain_type_kwargs = {"prompt": prompt}
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        PromptLayerChatOpenAI(temperature=0),
        chain_type="stuff",
        retriever=store.as_retriever(),
        chain_type_kwargs=chain_type_kwargs,
        reduce_k_below_max_tokens=True,
    )
    return chain


def lambda_handler(event, context):
    system_template = """
    Use the provided articles delimited by triple quotes to answer questions. If the answer cannot be found in the articles, write "I could not find an answer."
    When asked how much something costs, base your answer on ```https://portswigger.net/burp/enterprise/pricing```.
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
    ]
    prompt = ChatPromptTemplate.from_messages(messages)

    with open("faiss_store.pkl" "rb") as f:
        store = pickle.load(f)

    chain = get_chain(store, prompt)
    result = chain({"question": user_question})

    print(result)

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

    def respond(user_message, history)
        response = chain({"question": user_message, "history": history})
        print(response)
        # Append user message and response to chat history
        history.append((user_message, response["answer"]))
        return gr.update(value=""), history

    message.submit(respond, [message, chatbot], [message, chatbot], queue=False)
    submit.click(respond, [message, chatbot], [message, chatbot], queue=False)
    clear.click(lambda: None, None, chatbot, queue=False)

    demo.launch(share=False, server_name=("0.0.0.0"))
