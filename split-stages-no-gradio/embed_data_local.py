import pickle
import json
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings


json_file_path = "pages.json"
pkl_file_path = "faiss_store.pkl"
index_file_path = "doc.index"


def main():
    with open(json_file_path, "r") as f:
        pages = json.load(f)

    text_splitter = CharacterTextSplitter(chunk_size=1500, separator="\n")
    docs, metadatas = [], []
    for page in pages:
        splits = text_splitter.split_text(page["text"])
        docs.extend(splits)
        metadatas.extend([{"source": page["source"]}] * len(splits))

    store = FAISS.from_texts(
        docs,
        OpenAIEmbeddings(
            max_retries=100,
        ),
        metadatas=metadatas,
    )
    with open(pkl_file_path, "wb") as f:
        pickle.dump(store, f)


if __name__ == "__main__":
    main()
