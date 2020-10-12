from typing import Dict, List
from internaltypes import Feature, Grade
import pickle


def cache_essays(essays: List[Dict[Feature, int]], filename="essays.pickle"):
    """
    Serialiserar varje uppsatsvektor till filen essays.pickle för att inte behöva bearbeta varje gång programmet testas
    :param essays: En lista med dictionary. Varje dictionary innehåller ett värde för varje språkliga kännetecke
    :return:
    """
    pickle.dump(essays, open("cache\\%s" % filename, "wb"))


def cache_grades(grades: dict, filename="grades.pickle"):
    pickle.dump(grades, open("cache\\%s" % filename, "wb"))


def cache_machine_grades(grades: dict, filename="SVM_grades.pickle"):
    pickle.dump(grades, open("cache\\%s" % filename, "wb"))


def cache_kappas(kappas: Dict, filename="SVM_kappas.pickle"):
    pickle.dump(kappas, open("cache\\%s" % filename, "wb"))


def cache_features_kappas(SVM_kappas, LDAC_kappas):
    pickle.dump(SVM_kappas, open("cache\\SVM_features_kappas.pickle", "wb"))
    pickle.dump(LDAC_kappas, open("cache\\LDAC_features_kappas.pickle", "wb"))


def cache_classifier(classifier, filename="SVM_model.pickle"):
    pickle.dump(classifier, open("cache\\%s" % filename, "wb"))


def input_grades(essay_collection, filename="grades.pickle"):
    grades: dict = dict()
    print("Input on of the following grade for each essay", end=': ')
    [print(grade, end=' ') for grade in Grade.__members__.keys()]
    print()
    for essay in essay_collection:
        grades[essay["id"]] = Grade.__members__[input("Input grade for essay %s: " % essay["id"])]
    cache_grades(grades, filename)
    return grades


# Avserialiserar uppsatser i filen "essays.pickle" och returnerar en lista innehållandes en dict för varje uppsats
def read_essays(filename="essays.pickle") -> List[Dict[Feature, int]]:
    return pickle.load(open("cache\\%s" % filename, "rb"))


def read_grades(filename="grades.pickle") -> Dict[str, Grade]:
    return pickle.load(open("cache\\%s" % filename, "rb"))


def read_machine_grades() -> Dict[str, Grade]:
    return pickle.load(open("cache\\machine_grades.pickle", "rb"))


def read_kappas(filename="SVM_kappas.pickle"):
    return pickle.load(open("cache\\%s" % filename, "rb"))


def read_feature_kappas(filename="SVM_features_kappas.pickle") -> List:
    return pickle.load(open("cache\\%s" % filename, "rb"))

def read_classifier(filename="SVM_model.pickle"):
    return pickle.load(open("cache\\%s" % filename, "rb"))
