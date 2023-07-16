import yake
import unidecode


class KeyWordExtractor():
    
    def __init__(self):
        
        # Params
        self.config_params = {"language": "en",
                              "max_ngram_size": 3,
                              "deduplication_threshold": 0.5,
                              "numOfKeywords": 5}

    def extract_keywords_from_sentence(self,sentence):
        """
        This function will extractthe most important 
        sustantives from the sentence given.

        :param: sentence: sentence as string
        """

        kw_extractor = yake.KeywordExtractor(lan=config_params["language"], 
                                             n=config_params["max_ngram_size"],
                                             dedupLim=config_params["deduplication_threshold"],
                                             top=config_params["numOfKeywords"],
                                             features=None)


        # Storage all keywords
        keyword_list = []
        for item in  kw_extractor.extract_keywords(sentence):
            keyword_list.extend(item[0].split())

        #Clean repeated values

        return keyword_list
    
    def clean_list(self,lst):
        cleaned_list = []
        seen_names = set()

        for item in lst:
            # Convert string to lowercase and remove accents
            cleaned_item = self.remove_accents(item.lower())
            # Extract only the name from the string
            name = self.get_name(cleaned_item)

            if name not in seen_names:
                cleaned_list.append(name)
                seen_names.add(name)

        return cleaned_list
    
    def remove_accents(self,text):
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    
    def get_name(text):
        # Assuming the name is the first word before any whitespace
        return text.split()[0]
    