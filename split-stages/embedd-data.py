import pickle
import json
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

with open("pages.json", "r") as openfile:
    # Reading from json file
    pages = json.load(openfile)

text_splitter = CharacterTextSplitter(chunk_size=1500, separator="\n")
docs, metadatas = [], []
for page in pages:
    splits = text_splitter.split_text(page["text"])
    docs.extend(splits)
    metadatas.extend([{"source": page["source"]}] * len(splits))

store = FAISS.from_texts(
    docs, OpenAIEmbeddings(max_retries=100, show_progress_bar=True), metadatas=metadatas
)

with open("faiss_store.pkl", "wb") as f:
    pickle.dump(store, f)
