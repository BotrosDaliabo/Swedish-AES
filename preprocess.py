from math import log
import textract
from natsort import natsorted
from pathlib import Path
from typing import Final, List, Dict
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk
from os import listdir
import re
from pylanguagetool import api
from minmaxpair import MinMaxPair
from internaltypes import Feature, POSDict, FeatureNormaliseByFormula
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from io import StringIO
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter

# Matchar alla tecken förutom de som nämns och om tre eller fler mellanrumstecken följer efter varandra
regex = r'[^\w\d\'\"\”\“\;\-\–\?\:\,\/\n\.\’\´\%\(\)](\ {2})'
# Tar bort teckenkombinationen a.), a kan ersättas med vilken bokstav som helst. Tar även bort sluttecknet som pdf-extraheraren efterlämnar
regex_blacklist = r'|( [a-zA-Z].\))|'
integer_max: Final = 9223372036854775807
essay_collection: List[Dict] = []
# Ett par med första nummer som minimum och andra nummer som maximum sparas för varje kännetecken i syfte att senare normalisera värden
min_max_pairs: Dict = {}
stopwords_cache: List[str] = []


# en funktion för att undvika pdftotext fel, kommer tas bort när programmet är färdigt.
def pdf_to_text(pdfname):
    # PDFMiner boilerplate
    rsrcmgr = PDFResourceManager()
    sio = StringIO()
    device = TextConverter(rsrcmgr, sio, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # get text from file
    fp = open(pdfname, 'rb')
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
    fp.close()
    # Get text from StringIO
    text = sio.getvalue()
    # close objects
    device.close()
    sio.close()

    return text


def start(normalise=True, path="train_data/") -> List[Dict]:
    essay_collection.clear()
    min_max_pairs.clear()
    generate_min_max_pairs(min_max_pairs)
    cache_stopwords()
    directory = Path(path)
    dir_list = natsorted(listdir(directory))
    counter = 1
    print("Found %d documents" % len(dir_list))
    for filename in dir_list:
        print("Document number %d is being processed" % counter)
        counter += 1
        filepath = path + filename
        # här används PDFMiner
        if filename.endswith(".PDF"):
            text = pdf_to_text(filepath)
        else:
            text = textract.process(filepath).decode('UTF-8')
        text = re.sub(regex + regex_blacklist, '', text)
        no_of_sentences = count_sentences(text)
        text = clear_excessive_space(text)
        no_of_grammar_errors = count_grammatical_errors(text)
        word_list: List[str] = get_word_list(text)
        tokens = word_tokenize(text)
        pos_list = nltk.pos_tag(tokens)
        pos_distribution: POSDict = create_pos_dir(pos_list)
        essay_collection.append({"id": filename, Feature.no_of_tokens: len(tokens),
                                 Feature.no_of_words: len(word_list),
                                 Feature.no_of_sentences: no_of_sentences,
                                 Feature.no_of_grammatical_err: no_of_grammar_errors,
                                 Feature.no_of_verbs: pos_distribution[Feature.no_of_verbs],
                                 Feature.no_of_adjectives: pos_distribution[Feature.no_of_adjectives],
                                 Feature.no_of_adverbs: pos_distribution[Feature.no_of_adverbs],
                                 Feature.no_of_nouns: pos_distribution[Feature.no_of_nouns],
                                 Feature.average_word_length: count_average_word_length(word_list),
                                 Feature.no_of_pronouns: pos_distribution[Feature.no_of_pronouns],
                                 Feature.no_of_prepositions: pos_distribution[Feature.no_of_prepositions],
                                 Feature.no_of_participles: pos_distribution[Feature.no_of_participles],
                                 Feature.no_of_stopwords: count_stopwords(word_list),
                                 Feature.fourth_root_words: count_fourth_root(len(word_list)),
                                 Feature.no_of_unique_words: count_unique_words(word_list),
                                 Feature.no_of_long_words: count_long_words(word_list),
                                 Feature.OVIX: count_ovix(word_list),
                                 Feature.NR: count_NR(pos_distribution)})
        count_min_max()
    if normalise:
        normalise_values()
    return essay_collection


def generate_min_max_pairs(pairs: Dict):
    """
    :param pairs: en dictionary innehållandes minimum- och maximumvärde för varje språkligt kännetecken
    :return: Inget returvärde
    """
    for feature in Feature:
        pairs[feature] = MinMaxPair(integer_max, 0)


def get_word_list(text) -> list:
    return re.findall(r'[a-z|A-Z]+', text)


def count_sentences(text):
    return len(sent_tokenize(text))


def count_grammatical_errors(text):
    grammar = api.check(text, api_url='https://languagetool.org/api/v2/', lang='en',
                        disabled_rules="PROGRESSIVE_VERBS,CONFUSION_RULE,DASH_RULE,ENGLISH_WORD_REPEAT_BEGINNING_RULE,FROM_FORM,NO_SPACE_CLOSING_QUOTE",
                        disabled_categories="REDUNDANCY")
    return len(grammar["matches"])


def count_average_word_length(word_list: List[str]):
    """
    Beräknar summan av längden av alla ord dividerat med antalet ord. Svaret avrundas till 2 decimaler.
    :param word_list: En lista med ord
    :return: Genomsnittlig ordlängd bland orden i den inskickade listan. Svaret avrundas till 2 decimaler
    """
    counter = 0
    total_word_length = 0
    for word in word_list:
        counter += 1
        total_word_length += len(word)
    return round(total_word_length / counter, 2)


def count_min_max():
    """
    Uppdaterar minimum- och maximumvärde för varje kännetecken om den senaste inlagda uppsatsen innehåller ett minimum- eller maximumvärde
    :return:
    """
    essay = essay_collection[len(essay_collection) - 1]
    for feature in Feature:
        feature_value = essay[feature]
        if feature_value < min_max_pairs[feature]["min"]:
            min_max_pairs[feature]["min"] = feature_value
        if feature_value > min_max_pairs[feature]["max"]:
            min_max_pairs[feature]["max"] = feature_value


def normalise_values():
    """
    Normaliserar alla uppsater i essay_collection från start_index till slutet av listan essay_collection
    :param start_index: loopen i denna funktion loopar från detta index
    :return:
    """
    formula_features = FeatureNormaliseByFormula()
    for essay in essay_collection:
        # Vid normalisering genom att dividera med antalet ord ska nämnaren inte vara normaliserad
        non_normalised_no_words = essay[Feature.no_of_words]
        for feature in Feature:
            if feature in formula_features and ((min_max_pairs[feature]["max"] - min_max_pairs[feature]["min"]) != 0):
                essay[feature] = (essay[feature] - min_max_pairs[feature]["min"]) / (
                        min_max_pairs[feature]["max"] - min_max_pairs[feature]["min"])
            else:
                essay[feature] = essay[feature] / non_normalised_no_words


def create_pos_dir(pos_list) -> POSDict:
    pos_dir: POSDict = POSDict()
    for word, tag in pos_list:
        if tag.startswith("J"):
            pos_dir[Feature.no_of_adjectives] += 1
        elif tag.startswith("N"):
            pos_dir[Feature.no_of_nouns] += 1
        elif tag == "PRP" or tag == "PRP$":
            pos_dir[Feature.no_of_pronouns] += 1
        elif tag != "RP" and tag.startswith("R"):
            pos_dir[Feature.no_of_adverbs] += 1
        elif tag.startswith("VBN"):
            pos_dir[Feature.no_of_participles] += 1
        elif tag.startswith("V"):
            pos_dir[Feature.no_of_verbs] += 1
        elif tag.startswith("IN"):
            pos_dir[Feature.no_of_prepositions] += 1
        elif tag.startswith("W"):
            if tag == "WP" or tag == "WP$":
                pos_dir[Feature.no_of_pronouns] += 1
            elif tag == "WRB":
                pos_dir[Feature.no_of_adverbs] += 1

    return pos_dir


def clear_excessive_space(text):
    """
    Ser till att alla mellanrum i texten är maximalt 1 tecken långa
    """
    return re.sub(r"[\s]{2,}", ' ', text)


def count_long_words(word_list: List):
    """
    Beräknar antalet ord i den inskickade ordlistan vars längd överstiger 6 tecken
    :param wordlist: Lista innehållandes ord
    """
    counter = 0
    for word in word_list:
        if len(word) > 6:
            counter += 1
    return counter


def count_ovix(wordlist) -> float:
    """
    Beräknar ordvariationsindex
    """
    unique_words: float = count_unique_words(wordlist)
    denominator = log(2 - (log(unique_words) / log(len(wordlist))))
    return log(len(wordlist), 10) / denominator


def count_NR(pos_dict: POSDict) -> float:
    """
    Beräknar nominal ratio
    """
    return ((pos_dict[Feature.no_of_nouns] + pos_dict[Feature.no_of_prepositions] + pos_dict[
        Feature.no_of_participles]) /
            (pos_dict[Feature.no_of_pronouns] + pos_dict[Feature.no_of_adverbs] + pos_dict[Feature.no_of_verbs]))


def count_unique_words(word_list: List):
    wordset: set = set()
    for word in word_list:
        wordset.add(word)
    return len(wordset)


def count_fourth_root(length) -> float:
    return length ** 0.25


def count_stopwords(words: List):
    counter = 0
    global stopwords_cache
    for word in words:
        if word in stopwords_cache:
            counter += 1

    return counter


def cache_stopwords():
    global stopwords_cache
    file = open("allstopwords.txt", "r")
    stopwords_cache = file.read().split('\n')
    file.close()
