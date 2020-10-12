import unittest
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from internaltypes import Grade, GradingDict
import language_check


class TestFeatures(unittest.TestCase):
    wordcount = [(4, "I am a human"), (5, "abc, def, ghi (lmnopq). Rstu."), (47,
                                                                             "The General Data Protection Regulation (GDPR) is a comprehensive document that dictates which steps are necessary to undertake in order to protect the privacy of individuals living within the European Union (EU) or the European Economic Area (EEA) and transfer of personal data out of those territories."),
                 (60,
                  "The need for handling the data must outweigh any integrity issues or inconvenience for the subject, including the breach of rights and freedoms of the data subject, as stated in point f.) of article 6, GDPR. Furthermore, GDPR states in reason 47 that reasonable expectations of the subject should be considered when it comes to determining the scope of processing.")]
    sentences = [(4,
                  "An important part of GDPR regulation is article 5 that lists the principles relating to processing of data. The key focal points when it comes to processing are lawfulness, fairness and transparency towards the data subject. The information is required to be collected for a specified purpose and to be limited when it comes to width and time. Less is more should be a leading star when it comes to safe data processing."),
                 (3,
                  "The requirements for the material and territorial scope must be met, art. 2-3. The material scope requires the personal data to be processed wholly or partly by automated means or form part of a filing system or intend to form such system. "
                  "If the client is based physically, or to some extent is established within the Union, they are within the territorial scope."),
                 (5,
                  "All processing of data involving such information mentioned in art. 9.1 is unlawful, unless an exception in art. 9.2(a-j) is "
                  "applicable. Note that processing of national identification number is as well considered sensitive data, art. 87.")]

    abbreviations = [(1,
                      "The requirements for the material and territorial scope must be met, art. 2-3. The material scope requires the personal data to be processed wholly or partly by automated means or form part of a filing system or intend to form such system. "
                      "If the client is based physically, or to some extent is established within the Union, they are within the territorial scope."),
                     (3,
                      "All processing of data involving such information mentioned in art. 9.1 is unlawful, unless an exception in art. 9.2(a-j) is "
                      "applicable. Note that processing of national identification number is as well considered sensitive data, art. 87.")]

    unique_words = [(37,
                     "Such data considers for example racial or ethnic origin, personal health and sexual orientation. Although there are a number of legal grounds that justifies such sensitive personal data, as for example obligations under labour law, fundamental interests or data made public by the data subject.")]

    grades = {"memo1": Grade.VG, "memo2": Grade.G, "memo3": Grade.G, "memo4": Grade.G, "memo5": Grade.IG,
              "memo6": Grade.VG, "memo7": Grade.IG, "memo8": Grade.IG, "memo9": Grade.G, "memo10": Grade.G,
              "memo11": Grade.VG, "memo12": Grade.G, "memo13": Grade.G, "memo14": Grade.G}
    grading_dict = {Grade.IG: 3, Grade.G: 8, Grade.VG: 3}

    def test_count_words(self):
        for count, str in self.wordcount:
            self.assertEqual(len(re.findall(r'\w+', str)), count)

    # def test_count_sentences(self):
    #    for count, str in self.sentences:
    #        self.assertEqual(len(sent_tokenize(str)), count)

    def test_count_abbreviations(self):
        for count, str in self.abbreviations:
            self.assertEqual(len(re.findall("(\. [a-z|\d])+", str)), count)

    def test_pos_count(self):
        pos_list = nltk.pos_tag(word_tokenize(self.sentences[0][1]))
        expected = {"nouns": 17, "adjectives": 6, "verbs": 19, "adverbs": 4, "pronouns": 3}
        no_nouns = 0
        no_adjectives = 0
        no_verbs = 0
        no_adverbs = 0
        no_pronouns = 0
        for word, tag in pos_list:
            if tag.startswith("J"):
                no_adjectives += 1
            elif tag.startswith("N"):
                no_nouns += 1
            elif tag == "PRP" or tag == "PRP$":
                no_pronouns += 1
            elif tag != "RP" and tag.startswith("R"):
                no_adverbs += 1
            elif tag.startswith("V"):
                no_verbs += 1
            elif tag.startswith("W"):
                if tag == "WP" or tag == "WP$":
                    no_pronouns += 1
                elif tag == "WRB":
                    no_adverbs += 1
        result = {"nouns": no_nouns, "adjectives": no_adjectives, "verbs": no_verbs, "adverbs": no_adverbs,
                  "pronouns": no_pronouns}
        for tag, num in result.items():
            self.assertEqual(expected[tag], num)

    def test_unique_words(self):
        wordset: set = set()
        for pair in self.unique_words:
            for word in self.get_words(pair[1]):
                wordset.add(word)

    def test_create_grading_dict(self):
        grading_dict = GradingDict()
        for grade in self.grades.values():
            if grade == Grade.IG:
                grading_dict[Grade.IG] += 1
            elif grade == Grade.G:
                grading_dict[Grade.G] += 1
            else:
                grading_dict[Grade.VG] += 1
        self.assertEqual(grading_dict[Grade.IG], self.grading_dict[Grade.IG])
        self.assertEqual(grading_dict[Grade.G], self.grading_dict[Grade.G])
        self.assertEqual(grading_dict[Grade.VG], self.grading_dict[Grade.VG])

    def get_words(self, text: str) -> list:
        # noinspection PyMethodFirstArgAssignment
        text = text.lower()
        return re.findall(r'\w+', text)


if __name__ == '__main__':
    unittest.main()
