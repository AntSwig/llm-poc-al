import os

from langchain.chat_models import ChatOpenAI
from langchain.memory import ChatMessageHistory

chat = ChatOpenAI(temperature=0)
history = ChatMessageHistory()
history.add_ai_message("hi!")
history.add_user_message(
    "what pricing is currently available for burp suite enterprise ?"
)
history.messages
ai_response = chat(history.messages)
ai_response
history.add_ai_message(ai_response.content)
history.messages

print(history.messages)
