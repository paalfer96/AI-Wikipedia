import re
from fuzzywuzzy import fuzz

from haystack.document_stores import InMemoryDocumentStore


def welcome():
    welcome_message = "Welcome to AI Wikipedia!\n\n"
    instructions = [
        "Instructions:",
        "1 - Semantic Search:",
        "   Make a search about your favorite topic",
        "2 - Question Answering:",
        "   Add the exact URL or title if you want to make a question",
        "3 - Question Suggested:",
        "   In case you don't know what to ask, an AI model would help you",
    ]
    return "\n".join([welcome_message] + instructions)


def process(documents):
    document_list = []
    for docu in documents["documents"]:
        tmpString = docu.content
        tmpTitle = docu.meta["title"]
        tmpurl = docu.meta["url"]

        document_dict = {"title": tmpTitle, "url": tmpurl, "content": tmpString}

        document_list.append(document_dict)

    return document_list


def format_results(documents):
    formatted_text = ""
    for i, doc in enumerate(
        documents["documents"]
    ):  # Mostrar hasta los primeros 10 resultados
        formatted_text += f"Result {i + 1}:\n"
        formatted_text += f"Title: {doc.meta['title']}\n"
        formatted_text += f"URL: {doc.meta['url']}\n"
        formatted_text += f"Content: {doc.content}\n"
        formatted_text += "-" * 50 + "\n"
    return formatted_text


# Extract hash
def from_input_to_hash(document_store, input_text):
    # Check if the input resembles a URL
    url_pattern = r"^(https?://[^\s/$.?#].[^\s]*)$"
    is_url = re.match(url_pattern, input_text.lower())

    all_docs = document_store.get_all_documents()

    if is_url:
        all_urls = list(set([x.meta["url"] for x in all_docs]))

        cleaned_url = "".join(input_text.split()).strip()

        similarity_scores = {}
        for url in all_urls:
            similarity_scores[url] = fuzz.partial_ratio(
                cleaned_url.lower(), url.lower()
            )

        most_similar_url = max(similarity_scores, key=similarity_scores.get)

        for doc in all_docs:
            if doc.meta["url"] == most_similar_url:
                return doc.meta["hash"]
    else:
        all_titles = list(set([x.meta["title"] for x in all_docs]))
        cleaned_title = " ".join(input_text.split()).strip()

        similarity_scores = {}
        for title in all_titles:
            similarity_scores[title] = fuzz.partial_ratio(
                cleaned_title.lower(), title.lower()
            )

        most_similar_title = max(similarity_scores, key=similarity_scores.get)

        for doc in all_docs:
            if doc.meta["title"] == most_similar_title:
                return doc.meta["hash"]

    return None


def extract_text_from_article(document_store, docu_hash):
    all_docus = document_store.get_all_documents(filters={"hash": docu_hash})
    all_texts = []
    for doc in all_docus:
        all_texts.append({"content": doc.content, "meta": doc.meta})

    return all_texts
