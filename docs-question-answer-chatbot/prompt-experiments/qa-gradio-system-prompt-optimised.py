import argparse
import logging
import os
import pickle

import gradio as gr
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.vectorstores.faiss import FAISS

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
    # generate multiple different ways of asking the question based on the query
    logging.basicConfig()
    logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)
    retriever_from_llm = MultiQueryRetriever.from_llm(
        retriever=store.as_retriever(),
        llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", max_tokens=2048),
    )
    unique_docs = retriever_from_llm.get_relevant_documents(query="What is a bcheck")
    len(unique_docs)
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
# theme = "freddyaboulton/dracula_revamped"
# theme = "gstaff/xkcd"
# theme = "gradio/seafoam"

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
