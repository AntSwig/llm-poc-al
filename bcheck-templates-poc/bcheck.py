import logging
import os
import shutil

import requests
import xmltodict
from bs4 import BeautifulSoup
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import GitLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS

bcheck_loader = GitLoader(
    clone_url="https://github.com/PortSwigger/BChecks.git",
    repo_path="./bchecks",
    branch="main",
    file_filter=lambda file_path: file_path.endswith(".bcheck"),
)
bcheck_data = bcheck_loader.load()

(len(bcheck_data))


def extract_text_from(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.get_text()

    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


r = requests.get("https://portswigger.net/sitemap.xml")
xml = r.text
raw = xmltodict.parse(xml)

pages = []
for info in raw["urlset"]["url"]:
    # info example: {'loc': 'https://portswigger.net/burp/documentation...', 'lastmod': '2021-12-28'}
    url = info["loc"]
    if (
        "https://portswigger.net/burp/documentation/scanner/bchecks/bcheck-definition-reference"
        in url
    ):
        pages.append({"text": extract_text_from(url), "source": url})
print(pages[0])

text_splitter = CharacterTextSplitter(chunk_size=1500, separator="\n")
docs, metadatas = [], []
for page in pages:
    splits = text_splitter.split_text(page["text"])
    docs.extend(splits)
    metadatas.extend([{"source": page["source"]}] * len(splits))
    print(f"Split {page['source']} into {len(splits)} chunks")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=128,
    length_function=len,
)

texts = text_splitter.create_documents([bcheck_data[0].page_content])

documents = text_splitter.split_documents(texts)

db = FAISS.from_documents(documents, OpenAIEmbeddings())
# print(documents[0])
# for x in documents:
#     print(x.page_content)
#     print("\n=========================================\n")

vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings())
logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)
retriever_from_llm = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", max_tokens=2048),
)
unique_docs = retriever_from_llm.get_relevant_documents(query="What is a bcheck")
len(unique_docs)

query = "What is a bcheck"
docs = db.similarity_search(query)
print(docs[0].page_content)

shutil.rmtree("./bchecks")
