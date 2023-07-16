import re
import os
import json

from urllib.request import urlopen
from bs4 import BeautifulSoup



class Searcher:
    def __init__(self):

        # Get the directory path of the current script
        main_path = os.path.dirname(os.path.abspath(__file__))

        # Construct the full path to the config file
        config_path = os.path.join(main_path, "config", "config.json")

        # Read config
        with open(config_path, "r") as fh:
            self.config = json.load(fh)

        # other params
        self.re_pattern = r'title="([^"]*)"'

    def extract_articles(self, search, top_k=25):
        """
        This function will extract articles
        from wikipedia for a words given

        :param search: list of words
        :param top_k: number of articles to extract
        """

        # Extract URL to search
        searcher_url = self.create_search_element(self, search, top_k)

        # Extract article URL
        article_urls = self.create_article_url(searcher_url)

    def create_search_element(self, search, top_k):
        """
        This function will create the element
        to search and the final url

        :param search: list of words
        :param top_k: number of articles to extract
        """
        # Create search
        element = ""
        for item in search:
            if item == search[-1]:
                element += item
            else:
                element += item + "+OR+"

        return (
            self.config["main_url"].replace("$top_k", str(top_k))
            + element
            + self.config["last_url"]
        )
    
    def create_article_url(self,searcher_url):
        """
        This function will create the article link
        for a HTML given

        :param html: wikipedia searcher html
        """

        # Read URL
        html = urlopen(searcher_url).read()
        soup = BeautifulSoup(html, 'html.parser')
        sub_html = soup.find_all(class_="mw-search-result-heading")

        # Loop HTML
        article_urls = []
        for element in sub_html:
            match = re.search(self.re_pattern, str(element))
            if match:
                article_urls.append(self.config["article_url"]+match.group(1)) 
        

        return article_urls