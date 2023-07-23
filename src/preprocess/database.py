from haystack.document_stores import InMemoryDocumentStore
from haystack import Document

class DataBase:

    def __init__(self,use_bm25=True):
        
        # document store
        self.document_store = InMemoryDocumentStore(use_bm25=use_bm25)

    def generate_bbdd(self,texts):

        # Write
        self.document_store.write_documents(texts)
        return self.document_store