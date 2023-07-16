import nltk
import unidecode


class MainWordExtractor:

    """
    This class will take a sentece as an
    input and will extract main nous from it
    """

    def __init__(self):
        nltk.download("punkt", quiet=True)
        nltk.download("averaged_perceptron_tagger", quiet=True)

    def extract_mainwords_from_sentence(self, sentence):
        """
        This function will extractthe most important
        sustantives from the sentence given.

        :param: sentence: sentence as string
        """

        # Extract nouns
        category = nltk.pos_tag(nltk.word_tokenize(sentence))
        names = []
        for word in category:
            if word[1].startswith("NN"):
                names.append(str(self.remove_accents(word[0])))

        return self.get_unique_values(names)

    def get_unique_values(self, lst):
        """
        Returns a set containing only
        the unique values from the given list.

        :param: sentence: list of strings
        """

        return list(set(lst))

    def remove_accents(self, word):
        return unidecode.unidecode(word.lower().strip())
