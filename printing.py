from natsort import natsorted
from typing import List, Dict
import numpy as np
from sklearn.metrics import confusion_matrix

from evaluate import create_grading_dict
from internaltypes import Feature, Grade, GradingDict


def print_essays(essays: List[Dict[Feature, int]]):
    file = open("essays.txt", "a")
    for essay in essays:
        for key in essay:
            if key == "id":
                file.write("File: %s\n" % essay[key])
            else:
                file.write("%s: %.2f\n" % (key.name, essay[key]))
    file.close()


def print_text(text: str):
    file = open("text.txt", "a")
    file.write(text)
    file.close()


def print_grades(machine: Dict[str, Grade], teacher: Dict[str, Grade], filename="SVM_grades.csv"):
    with open("csv-files\\%s" % filename, "a") as file:
        file.truncate(0)
        file.write("Uppsats;Lärare;Maskin;Enighet\n")
        for key in natsorted(teacher.keys()):
            file.write("%s;%s;%s;%s\n" % (
                key, teacher[key].name, machine[key].name, "Ja" if teacher[key] == machine[key] else "Nej"))


def print_grade_table(machine: Dict[str, Grade], teacher: Dict[str, Grade], filename="SVM_grade_table.csv"):
    with open("csv-files\\%s" % filename, "a") as file:
        file.truncate(0)
        machine_grades = create_grading_dict(machine)
        teacher_grades = create_grading_dict(teacher)
        file.write("Betyg;Lärare;Maskin\n")
        for key in teacher_grades.keys():
            file.write("%s;%s;%s\n" % (key.name, teacher_grades[key], machine_grades[key]))


def print_kappas(SVM_kappa, LDAC_kappa):
    with open("csv-files\\kappas.csv", "a") as file:
        file.truncate(0)
        file.write(";Kappa\nSVM;%f\nLDAC;%f" % (SVM_kappa, LDAC_kappa))


def print_experiment_results(results: tuple):
    with open("csv-files\\experiment_SVM.csv", "a") as file:
        file.truncate(0)
        file.write("Kännetecken;Kappavärde\n")
        for item in results[0]:
            file.write("%s;%f\n" % (item[0], item[1]))
    with open("csv-files\\experiment_LDAC.csv", "a") as file:
        file.truncate(0)
        file.write("Kännetecken;Kappavärde\n")
        for item in results[1]:
            file.write("%s;%f\n" % (item[0], item[1]))


def print_f_scores(f_scores: List):
    with open("csv-files\\f-scores.csv", "a") as file:
        file.truncate(0)
        file.write("Kännetecken;F-score\n")
        for tuple in natsorted(f_scores, reverse=True, key=lambda tuple: tuple[1]):
            file.write("%s;%f\n" % (tuple[0], tuple[1]))


def print_feature_count(feature_dict_tuple: tuple):
    """
    Skriver ut hur ofta varje kännetecken förekommer i delmängderna.
    :param feature_dict_tuple: Första värdet är dictionary innehållandes förekomsten per kännetecken för SVM, andra värdet är för LDAC
    """
    with open("csv-files\\feature_count_top_10.csv", "a") as file:
        file.truncate(0)
        file.write("Kännetecken;Förekomst för SVM;Förekomst för LDAC\n")
        # Anropar zip() för att kunna iterera över båda dictionary samtidigt
        for (k, v), (k2, v2) in zip(feature_dict_tuple[0].items(), feature_dict_tuple[1].items()):
            file.write("%s;%d;%d\n" % (k, v, v2))


def print_confusion_matrix(teacher: Dict[str, Grade], SVM: Dict[str, Grade], LDAC:  Dict[str, Grade]):
    actual = []
    svm = []
    ldac = []
    for essay in teacher.keys():
        actual.append(teacher[essay].value)
        svm.append(SVM[essay].value)
        ldac.append(LDAC[essay].value)

    svm_matrix = confusion_matrix(actual, svm)
    ldac_matrix = confusion_matrix(actual, ldac)
    print("SVM")
    print(svm_matrix)
    print("LDAC:")
    print(ldac_matrix)

    with open("csv-files\\confusion_matrix.csv", "a") as file:
        file.truncate(0)
        file.write("SVM;;Maskin;;;LDAC;;Maskin;;\n")
        file.write("Lärare;IG;G;VG;;Lärare;IG;G;VG\n")
        file.write("IG;%d;%d;%d;;IG;%d;%d;%d\n" % (svm_matrix[0][0], svm_matrix[0][1], svm_matrix[0][2],
                                                   ldac_matrix[0][0], ldac_matrix[0][1], ldac_matrix[0][2]))
        file.write("G;%d;%d;%d;;G;%d;%d;%d\n" % (svm_matrix[1][0], svm_matrix[1][1], svm_matrix[1][2],
                                                   ldac_matrix[1][0], ldac_matrix[1][1], ldac_matrix[1][2]))
        file.write("VG;%d;%d;%d;;VG;%d;%d;%d\n" % (svm_matrix[2][0], svm_matrix[2][1], svm_matrix[2][2],
                                                   ldac_matrix[2][0], ldac_matrix[2][1], ldac_matrix[2][2]))


def print_feature_kappas(SVM_kappas: dict, LDAC_kappas: dict):
    with open("csv-files\\feature_kappas.csv", "a") as file:
        file.truncate(0)
        file.write("Kännetecken;Kappavärde för SVM;Kappavärde för LDAC\n")
        for feature in SVM_kappas.keys():
            file.write("%s;%f;%f\n" % (feature.name, SVM_kappas[feature], LDAC_kappas[feature]))
