from enum import Enum

class Grade(Enum):
    IG = 0
    G = 1
    VG = 2

# Syftet med att skapa egen version av datastrukturen dictionary är kunna fördefiniera nycklarna i datastrukturen, en funktion
# som tar emot en parameter med denna datatyp vet vilka nycklar som finns i dictionary
class GradingDict(dict):
    def __init__(self):
        super().__init__()
        self[Grade.IG] = 0
        self[Grade.G] = 0
        self[Grade.VG] = 0

# Part of speech dictionary, innehåller fördefinierade nycklar vilket gör att funktioner som tar emot en POSDict vet vilka nycklar
# som finns och behöver inte kontrollera
class POSDict(dict):
    def __init__(self):
        super().__init__()
        self[Feature.no_of_verbs] = 0
        self[Feature.no_of_nouns] = 0
        self[Feature.no_of_pronouns] = 0
        self[Feature.no_of_prepositions] = 0
        self[Feature.no_of_prepositions] = 0
        self[Feature.no_of_participles] = 0
        self[Feature.no_of_adjectives] = 0
        self[Feature.no_of_adverbs] = 0
        self[Feature.no_of_prepositions] = 0


# Innehåller alla kännetecken som ska normaliseras enligt formel, istället för att divideras med antalet ord
class FeatureNormaliseByFormula(dict):
    def __init__(self):
        super().__init__()
        self[Feature.no_of_words] = Feature.no_of_words
        self[Feature.no_of_tokens] = Feature.no_of_tokens
        self[Feature.fourth_root_words] = Feature.fourth_root_words
        self[Feature.OVIX] = Feature.OVIX
        self[Feature.NR] = Feature.NR


class Feature(Enum):
    no_of_tokens = "no_of_tokens"
    no_of_words = "no_of_words"
    no_of_sentences = "no_of_sentences"
    no_of_grammatical_err = "no_of_grammatical_err"
    average_word_length = "average_word_length"
    no_of_verbs = "no_of_verbs"
    no_of_pronouns = "no_of_pronouns"
    no_of_prepositions = "no_of_prepositions"
    no_of_participles = "no_of_participles"
    no_of_adjectives = "no_of_adjectives"
    no_of_adverbs = "no_of_adverbs"
    no_of_nouns = "no_of_nouns"
    no_of_stopwords = "no_of_stopwords"
    fourth_root_words = "fourth_root_words"
    no_of_unique_words = "no_of_unique_words"
    no_of_long_words = "no_of_long_words"
    OVIX = "OVIX"
    NR = "NR"