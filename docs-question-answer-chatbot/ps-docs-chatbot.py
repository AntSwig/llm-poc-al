import os
import pickle

import requests
import xmltodict
from bs4 import BeautifulSoup
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS


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
    if "https://portswigger.net" in url:
        pages.append({"text": extract_text_from(url), "source": url})
print(pages[0])

text_splitter = CharacterTextSplitter(chunk_size=1500, separator="\n")
docs, metadatas = [], []
for page in pages:
    splits = text_splitter.split_text(page["text"])
    docs.extend(splits)
    metadatas.extend([{"source": page["source"]}] * len(splits))
    print(f"Split {page['source']} into {len(splits)} chunks")

store = FAISS.from_texts(docs, OpenAIEmbeddings(), metadatas=metadatas)
with open("faiss_store.pkl", "wb") as f:
    pickle.dump(store, f)
