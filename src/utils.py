import os
import json

from haystack.document_stores import InMemoryDocumentStore


def read_configuration(config_filename="config.json"):
    # Get the directory path of the current script
    main_path = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the config file
    config_path = os.path.join(main_path, "config", config_filename)

    # Read config
    with open(config_path, "r") as fh:
        config = json.load(fh)

    return config


def filter_document_store(document_store, document_hash):
    """
    Function to filter the document store in order to
    extract just documents with an specific hash
    """

    filtered_docs = []
    for document in document_store.get_all_documents():
        if document.meta["hash"] == document_hash:
            filtered_docs.append(document)

    filtered_document_store = InMemoryDocumentStore(use_bm25=True)
    filtered_document_store.write_documents(filtered_docs)
    return filtered_document_store
