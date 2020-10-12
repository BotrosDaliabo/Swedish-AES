# Skriptet innehåller funktioner för att behandla en enda fil, skriptet används enbart för testning
import textract
import re
import debug
from pylanguagetool import api

# Tecken som inte är: ett ord, en siffra, en apostrof, ett citattecken, ett bindestreck, ett tankestreck
regex = r'[^\w\d\'\"\”\“\;\-\–\?\:\,\/\n\.\’\´\%\(\)](\ {2})'
regex_blacklist = r'|( [a-zA-Z].\))|'

def readfile():
    #filename = input("Enter name of file: ")
    filename = "memo24.DOCX"
    filepath = "unprocessed/" + filename
    text = textract.process(filepath).decode('UTF-8')
    text = re.sub(regex + regex_blacklist, '', text)
    debug.print_text(text)
    grammar = api.check(text, api_url='https://languagetool.org/api/v2/', lang='en',
                        disabled_rules="PROGRESSIVE_VERBS,CONFUSION_RULE,DASH_RULE,ENGLISH_WORD_REPEAT_BEGINNING_RULE,FROM_FORM,NO_SPACE_CLOSING_QUOTE", disabled_categories="REDUNDANCY")
    for match in grammar["matches"]:
        print(match)
    #print(len(grammar["matches"]))

def remove_abbreviations(text):
    return str.replace(text, "art.", "article")

def clear_parenthesis(text):
    return re.sub(r"\s\(.*?\)+", '', text)

def clear_excessive_space(text):
    return re.sub(r"[\s]{2,}", ' ', text)

# korrigerar felaktig inläsning av 's, t.ex it's
def correct_possessive_pronouns(text):
    return re.sub(r"[â]+", '\'', text)

def remove_quotes_mark(text):
    return re.sub(r"[“”\"]+", '', text)

if __name__ == '__main__': readfile()