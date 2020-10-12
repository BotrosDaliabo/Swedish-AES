# Startfilen för programmet, koordinerar programflödet
import preprocess
import printing
from evaluate import calculate_kappa
from internaltypes import Feature, Grade
from assessment import train_in_svm, train_in_ldac, predict_essay
import cache_manager
from typing import List, Dict
from os import path

grade_dict = Dict[str, Grade]
array = []
SVM_grades: Dict[str, Grade]
LDAC_grades: Dict[str, Grade]
kappas: tuple = ()
global kappa_all_features

def print_results():
    printing.print_grades(machine=SVM_grades, teacher=grade_dict)
    printing.print_grades(machine=LDAC_grades, teacher=grade_dict, filename="LDAC_grades.csv")
    printing.print_grade_table(machine=SVM_grades, teacher=grade_dict)
    printing.print_grade_table(machine=LDAC_grades, teacher=grade_dict, filename="LDAC_grade_table.csv")
    printing.print_kappas(kappa_all_features[0], kappa_all_features[1])

def evaluate(SVM_grades, LDAC_grades) -> tuple:
    kappa_svm = calculate_kappa(grade_dict, SVM_grades)
    kappa_ldac = calculate_kappa(grade_dict, LDAC_grades)
    return (kappa_svm, kappa_ldac)


def train_all_features():
    global SVM_grades, LDAC_grades, kappa_all_features
    """
    Tränar klassificeraren med alla språkliga kännetecken
    """
    features = Feature.__members__.values()
    features_list: List[Feature] = list(features)
    SVM_grades = train_in_svm(essay_collection, features_list, grade_dict)
    LDAC_grades = train_in_ldac(essay_collection, features_list, grade_dict)
    kappa_all_features = evaluate(SVM_grades, LDAC_grades)
    if not path.exists("csv-files\\f-scores.csv"):
        printing.print_f_scores(predict.calculate_f_scores(essay_collection, features_list, grade_dict))
    if not path.exists("cache\\SVM_grades.pickle.pickle") or not path.exists("cache\\LDAC_grades.pickle"):
        cache_manager.cache_machine_grades(SVM_grades)
        cache_manager.cache_machine_grades(LDAC_grades, "LDAC_grades.pickle")


def train_each_feature() -> (dict, dict):
    """
    Tränar SVM och LDAC kännetecken för kännetecken
    :return:
    """
    features = Feature.__members__.values()
    features_list: List[Feature] = list(features)
    SVM_grades = {}
    LDAC_grades = {}
    for feature in features_list:
        SVM_grades[feature] = train_in_svm(essay_collection, [feature], grade_dict)
        LDAC_grades[feature] = train_in_ldac(essay_collection, [feature], grade_dict)

    return (SVM_grades, LDAC_grades)


def evaluate_each_feature(SVM_grades: dict, LDAC_grades: dict) -> (dict, dict):
    feature_kappas_SVM = {}
    feature_kappas_LDAC = {}
    for feature in SVM_grades.keys():
        feature_kappas_SVM[feature] = calculate_kappa(grade_dict, SVM_grades[feature])
        feature_kappas_LDAC[feature] = calculate_kappa(grade_dict, LDAC_grades[feature])

    return (feature_kappas_SVM, feature_kappas_LDAC)


if __name__ == '__main__':
    global kappa_all_features
    #if not path.exists("cache\\SVM_features_kappas.pickle") or not path.exists("cache\\LDAC_features_kappas.pickle"):
    #    experiment.start_experiment(teacher_grades=grade_dict, essays=essay_collection)
    if not path.exists("cache\\SVM_model.pickle") or not path.exists("cache\\LDAC_model.pickle"):
        if path.exists("cache\\essays.pickle"):
            essay_collection = cache_manager.read_essays()
        else:
            essay_collection = preprocess.start()
            cache_manager.cache_essays(essay_collection)
        if path.exists("cache\\grades.pickle"):
            grade_dict = cache_manager.read_grades()
        else:
            grade_dict = cache_manager.input_grades(essay_collection)
        train_all_features()
        feature_grades = train_each_feature()
        feature_kappas = evaluate_each_feature(feature_grades[0], feature_grades[1])
        printing.print_feature_kappas(feature_kappas[0], feature_kappas[1])
    else:
        svm = cache_manager.read_classifier()
        ldac = cache_manager.read_classifier("LDAC_model.pickle")
        essay_vector = preprocess.start(normalise=True,path="essays_to_test/")
        if (len(essay_vector) >= 1):
            for essay in essay_vector:
                predictions = predict_essay(essay_vector[0], list(Feature.__members__.values()), svm, ldac)
                print("Essay: %s  SVM Grade: %s  LDAC Grade: %s" % (essay["id"], predictions[0].name, predictions[1].name))
