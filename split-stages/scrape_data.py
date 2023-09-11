import requests
import xmltodict
import json
import warnings
from bs4 import BeautifulSoup, GuessedAtParserWarning


def extract_text_from(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    warnings.filterwarnings("ignore", category=GuessedAtParserWarning)
    text = soup.get_text()

    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


r = requests.get("https://portswigger.net/sitemap.xml")
xml = r.text
raw = xmltodict.parse(xml)

pages = []
for info in raw["urlset"]["url"]:
    if not info["loc"].startswith("https://portswigger.net/daily-swig"):
        url = info["loc"]
        if "https://portswigger.net" in url:
            pages.append({"text": extract_text_from(url), "source": url})

with open("pages.json", "w") as f:
    json.dump(pages, f)
