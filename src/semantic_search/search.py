from haystack.nodes import BM25Retriever, SentenceTransformersRanker
from haystack import Pipeline

import os
import json


class SemanticSearch:

    def __init__(self , document_store):

        # Get the directory path of the current script
        main_path = os.path.dirname(os.path.abspath(__file__))

        # Construct the full path to the config file
        config_path = os.path.join(main_path, "config", "config.json")

        # Read config
        with open(config_path, "r") as fh:
            self.config = json.load(fh)    

        # document store
        self.document_store = document_store

        # Load componentes
        self.retriever = BM25Retriever(self.document_store)
        self.ranker = SentenceTransformersRanker(model_name_or_path=self.config["model_name"])

        # Define Pipeline
        self.search_pipeline = Pipeline()
        self.search_pipeline.add_node(component=self.retriever, name="BM25Retriever", inputs=["Query"])
        self.search_pipeline.add_node(component=self.ranker, name="Ranker", inputs=["BM25Retriever"])
    
    def search(self, query):

        # Create the search
        return self.search_pipeline.run(query=query, params = self.config["params"])