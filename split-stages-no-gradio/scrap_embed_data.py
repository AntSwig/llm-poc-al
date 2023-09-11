import requests
import xmltodict
import pickle
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from bs4 import BeautifulSoup
import warnings
from bs4 import GuessedAtParserWarning


json_file_path = "pages.json"
json_file_path = "pages.json"
pkl_file_path = "faiss_store.pkl"
index_file_path = "doc.index"


def extract_text_from(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, features="html.parser")
    warnings.filterwarnings("ignore", category=GuessedAtParserWarning)
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


def scrape_data() -> list:
    r = requests.get("https://portswigger.net/sitemap.xml")
    xml = r.text
    raw = xmltodict.parse(xml)

    pages = []
    for info in raw["urlset"]["url"]:
        if not info["loc"].startswith("https://portswigger.net/daily-swig"):
            url = info["loc"]
            if "https://portswigger.net" in url:
                pages.append({"text": extract_text_from(url), "source": url})
    return pages


def embed_data(pages: list):
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
    scrape_output = scrape_data()
    embed_data(scrape_output)
