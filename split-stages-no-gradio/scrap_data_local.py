import requests
import xmltodict
import json
from bs4 import BeautifulSoup
import warnings
from bs4 import GuessedAtParserWarning


json_file_path = "pages.json"


def extract_text_from(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, features="html.parser")
    warnings.filterwarnings("ignore", category=GuessedAtParserWarning)
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


def main():
    r = requests.get("https://portswigger.net/sitemap.xml")
    xml = r.text
    raw = xmltodict.parse(xml)

    pages = []
    for info in raw["urlset"]["url"]:
        if not info["loc"].startswith("https://portswigger.net/daily-swig"):
            url = info["loc"]
            if "https://portswigger.net" in url:
                pages.append({"text": extract_text_from(url), "source": url})

    with open(json_file_path, "w") as f:
        json.dump(pages, f)


if __name__ == "__main__":
    main()
