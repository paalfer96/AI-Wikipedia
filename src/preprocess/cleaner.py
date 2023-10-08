# Libraries
import re
import json
import hashlib
import os

from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup
from tqdm import tqdm


class TextCleaner:
    def __init__(self):
        # Get the directory path of the current script
        main_path = os.path.dirname(os.path.abspath(__file__))

        # Construct the full path to the config file
        config_path = os.path.join(main_path, "config", "config.json")

        # Read config
        with open(config_path, "r") as fh:
            self.config = json.load(fh)

        # Other params
        self.re_pattern = r"\[\d+\]"
        self.splits = []

    def from_urls_to_dict(self, search_url):
        # Loop cleaning the text for each url
        texts = []
        for url in search_url:
            tmpText, tmpTitle = self.clean_url_text(url)
            texts_dict = {"text": tmpText, "title": tmpTitle, "url": url}
            texts.append(texts_dict)

        # Generate a a list of dictionaries
        return self.generate_splits(texts)

    def clean_url_text(self, url):
        # Acess URL
        cleaned_url, title = self.parse_url(url)
        page = urlopen(cleaned_url).read()
        soup = BeautifulSoup(page, "lxml")

        # Extract the plain text content from paragraphs
        paras = []
        for paragraph in soup.find_all("p"):
            paras.append(str(paragraph.text))

        # Extract text from paragraph headers
        heads = []
        for head in soup.find_all("span", attrs={"mw-headline"}):
            heads.append(str(head.text))

        # Interleave paragraphs & headers
        text = [val for pair in zip(paras, heads) for val in pair]
        text = " ".join(text)

        # Clean text
        text = (
            re.sub(str(self.re_pattern), "", text)
            .replace("\xa0", " ")
            .replace("\n", " ")
            .lower()
            .strip()
        )

        return text, title

    def parse_url(self, url):
        title = url[url.find("wiki/") :].replace("wiki/", "")
        return url[: url.find("wiki/")] + "wiki/" + quote(title), title

    def generate_splits(self, text_list):
        for text_dict in tqdm(text_list):
            tmpTitle = text_dict["title"]
            tmpText = text_dict["text"]
            tmpUrl = text_dict["url"]
            chunks = self.split_text_into_chunks(tmpText)
            for chunk in chunks:
                content = " ".join(chunk)
                hash_value = hashlib.sha256(content.encode()).hexdigest()
                split = {
                    "content": content,
                    "meta": {
                        "title": tmpTitle,
                        "url": tmpUrl,
                        "split_id": hash_value,
                        "hash": hashlib.sha256(tmpText.encode()).hexdigest(),
                    },
                }
                self.splits.append(split)
        return self.splits

    def split_text_into_chunks(self, text):
        words = text.split()
        return [
            words[i : i + self.config["chunk_size"]]
            for i in range(0, len(words), self.config["chunk_size"])
        ]
