# Libraries
import sys
import os

import gradio as gr

import warnings

warnings.filterwarnings("ignore")


# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Append the 'src' directory to the Python path
src_dir = os.path.join(current_dir, "src")
sys.path.append(src_dir)

# Local imports
from wrapper.mainwords import MainWordExtractor
from wrapper.searcher import Searcher
from preprocess.cleaner import TextCleaner
from preprocess.database import DataBase
from semantic_search.search import SemanticSearch
from question_answering.extractive_qa import ExtractiveQA
from question_generation.question_gen import QuestionGenerator

# Import utils functions
from app_utils import welcome
from app_utils import format_results
from app_utils import from_input_to_hash
from app_utils import extract_text_from_article


# Search
def make_search(query):
    global document_store
    # definitions
    extractor = MainWordExtractor()
    ss = Searcher()
    # apply
    search = extractor.extract_mainwords_from_sentence(sentence=query)
    url = ss.create_search_element(search, top_k=15)
    search_url = ss.create_article_url(url)

    # definitions and apply
    cleaner = TextCleaner()
    bbdd = cleaner.from_urls_to_dict(search_url)

    # definitions and apply
    database = DataBase()
    document_store = database.generate_bbdd(bbdd)

    # definitions
    searcher = SemanticSearch(document_store=document_store)
    # apply
    documents = searcher.search(query=query)

    return format_results(documents)


# QA
def make_question(query, input_text):
    global document_store
    global document_hash
    qa = ExtractiveQA(document_store=document_store)

    document_hash = from_input_to_hash(
        document_store=document_store, input_text=input_text
    )

    responses = qa.answer(question=query, document_hash=document_hash)
    return responses["answer"]


# question suggested
def make_suggestion(input_text):
    global document_store
    global document_hash

    question_gen = QuestionGenerator()
    cleanedInput_text = input_text.strip()
    if cleanedInput_text == "":
        all_texts = extract_text_from_article(document_store, document_hash)
        questions = question_gen.generate_questions(
            texts=all_texts, article_hash=document_hash, top_k=3
        )
        return "\n".join(questions)
    else:
        docu_hash = from_input_to_hash(
            document_store=document_store, input_text=input_text
        )

        all_texts = extract_text_from_article(document_store, docu_hash)
        questions = question_gen.generate_questions(
            texts=all_texts, article_hash=docu_hash, top_k=3
        )
        return "\n".join(questions)


if __name__ == "__main__":
    # Interface para la bienvenida
    welcome_app = gr.Interface(fn=welcome, inputs=None, outputs="text", title="Welcome")

    semantic_search_app = gr.Interface(
        fn=make_search,
        inputs="text",
        outputs="text",
        title="Semantic Search",
        theme="dark",
    )

    question_answer_app = gr.Interface(
        fn=make_question,
        inputs=[
            gr.inputs.Textbox(label="write your question"),
            gr.inputs.Textbox(label="Add title or url"),
        ],
        outputs="text",
        title="Question Answering",
        theme="dark",
    )

    question_suggestion_app = gr.Interface(
        fn=make_suggestion,
        inputs=gr.inputs.Textbox(label="Enter the title or url"),
        outputs="text",
        title="Question Suggested",
        theme="dark",
    )

    # Ejecutar la aplicación Gradio
    demo = gr.TabbedInterface(
        [
            welcome_app,
            semantic_search_app,
            question_answer_app,
            question_suggestion_app,
        ],
        ["Welcome", "Semantic Search", "Question Answering", "Question Suggested"],
    )
    demo.launch(share=True)
