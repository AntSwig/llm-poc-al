import os

from langchain import LLMChain
from langchain.llms import OpenAI
# Chat specific components
from langchain.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate

template = """
You are a chatbot that is unhelpful.
Your goal is to not help the user but only make jokes.
Take what the user is saying and make a joke out of it

{chat_history}
Human: {human_input}
Chatbot:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"], template=template
)
memory = ConversationBufferMemory(memory_key="chat_history")

llm_chain = LLMChain(
    llm=OpenAI(),
    prompt=prompt,
    verbose=True,
    memory=memory,
)

llm_chain.predict(human_input="Is a pear a fruit or vegetable?")
