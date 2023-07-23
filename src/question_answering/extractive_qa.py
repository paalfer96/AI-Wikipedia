import os
import json

from haystack.pipelines import ExtractiveQAPipeline
from haystack.nodes import BM25Retriever, TransformersReader

from utils import read_configuration,filter_document_store


class ExtractiveQA:

    def __init__(self,document_store):

        self.config =  read_configuration(config_filename="qa_config.json")

        # document store
        self.document_store = document_store

        # Load componentes
        self.retriever = BM25Retriever(self.document_store)
        self.reader = TransformersReader(model_name_or_path= self.config["extractive_model_name"])
        
    
    def answer(self,question, document_hash):
        
        # Filter document store based on hash
        filtered_document_store = filter_document_store(document_store=self.document_store,
                                                        document_hash=document_hash)

        # Execution
        retrieved_documents  = self.retriever.retrieve(query=question,document_store=filtered_document_store)
        response = self.reader.predict(query=question, documents=retrieved_documents)

        # Extract response
        res = response["answers"][0]
        return {"answer": res.answer, "context": res.context}
