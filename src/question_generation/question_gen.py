import json
import os
import pandas as pd

from tqdm import tqdm
from transformers import T5ForConditionalGeneration, T5Tokenizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class QuestionGenerator:

    def __init__(self):

        # Get the directory path of the current script
        main_path = os.path.dirname(os.path.abspath(__file__))

        # Construct the full path to the config file
        config_path = os.path.join(main_path, "config", "config.json")

        # Read config
        with open(config_path, "r") as fh:
            self.config = json.load(fh)    

        # Load the model
        self.tokenizer = T5Tokenizer.from_pretrained(self.config["model_name"])
        self.model = T5ForConditionalGeneration.from_pretrained(self.config["model_name"])

    def generate_questions(self,texts,article_hash,top_k):

        # General lists
        content_list = []
        hash_list = []
        question_list = []
        cos_sim = []
        
        # Filter dictionary
        filtered_list = [item for item in texts
                          if "meta" in item and "hash" in item["meta"]
                            and item["meta"]["hash"] == article_hash]

        # Generate question for each paragraph
        for item in tqdm(filtered_list):
            try:
                questions = self.run_model(text=item["content"], top_k=top_k)
            except:
                raise ValueError('top_k must be lower than 5')
            for question in questions:
                content_list.append(item["content"])
                hash_list.append(item["meta"]["hash"])
                question_list.append(question)
                cos_sim.append(self.calculate_cosine_similarity(item["content"],question))
            
        # Create the dictionary
        df_dict = {
            "content": content_list,
            "hash": hash_list,
            "question": question_list,
            "cos_sim": cos_sim
        }

        # Create the dataframe and preprocess
        df = self.remove_similar_questions(data=pd.DataFrame(df_dict), threshold=self.config["threshold"])

        # filter
        df = df[:top_k]

        return list(df["question"])
    
    def remove_similar_questions(self,data, threshold):
        # Vectorize the questions using TF-IDF
        vectorizer = TfidfVectorizer(lowercase=True)
        vectors = vectorizer.fit_transform(data['question'])

        # Calculate cosine similarity between question vectors
        similarity_matrix = cosine_similarity(vectors, vectors)

        # Filter out similar questions
        filtered_indices = set()
        num_questions = len(data)
        for i in range(num_questions):
            for j in range(i+1, num_questions):
                if similarity_matrix[i][j] >= threshold:
                    filtered_indices.add(i)
                    filtered_indices.add(j)

        # Remove similar questions from the dataframe
        filtered_data = data.drop(filtered_indices).sort_values(by="cos_sim",ascending=False).reset_index(drop=True)

        return filtered_data

    def run_model(self,text,top_k):

        input_ids = self.tokenizer.encode(text, return_tensors="pt")
        res = self.model.generate(
            input_ids,
            num_return_sequences=top_k,
            num_beams=self.config["num_beams"],
            max_length=self.config["max_length"],
            early_stopping=True
        )
        output = self.tokenizer.batch_decode(res, skip_special_tokens=True)
        return output 
    
    def calculate_cosine_similarity(self,text1, text2):
            
            corpus = [text1, text2]
            vectorizer = CountVectorizer().fit_transform(corpus)
            vectors = vectorizer.toarray()
            similarity = cosine_similarity(vectors[0].reshape(1, -1), vectors[1].reshape(1, -1))
            return similarity[0][0]
    
