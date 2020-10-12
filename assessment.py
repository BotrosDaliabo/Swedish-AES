from sklearn import svm, feature_selection
from typing import Dict, List
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import numpy as np
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.preprocessing import LabelEncoder

import cache_manager
from internaltypes import Feature, Grade

param={'kernel': ('linear','poly','rbf','sigmoid'),'C':[0.0001,1000,1],'gamma':('auto','scale')}
svm_classifier = None

def extract_essay_ids(indexes, list) -> List[str]:
    sub_list = []
    for index in indexes:
        sub_list.append(list[index]["id"])
    return sub_list


def calculate_f_scores(essays: List[Dict[Feature, int]], features: List[Feature], grading_dict: Dict[str, Grade]):
    feature_values = create_feature_matrix(essays, features)
    labels = np.array([grade.value for grade in grading_dict.values()])
    kbest = feature_selection.SelectKBest(k=len(features))
    kbest.fit(feature_values, labels)
    le = LabelEncoder()
    features_names = [feature.name for feature in features]
    feature_normalised = le.fit(features_names).transform(features_names)
    names = feature_normalised[kbest.get_support()]
    scores = kbest.scores_[kbest.get_support()]
    names_scores = list(zip(le.inverse_transform(names), scores))


    return names_scores


def create_feature_matrix(essays: List[Dict[Feature, int]], features: List[Feature]):
    feature_values = np.arange(len(essays) * len(features), dtype=float).reshape(len(essays), len(features))
    row = 0
    for essay in essays:
        col = 0
        for feature in features:
            feature_values[row][col] = essay[feature]
            col += 1
        row += 1

    return feature_values


def tune_svm_classifier(feature_values, labels):
    global svm_classifier
    """
    Implementerar hyperparameter tuning m.h.a korsvalidering och skapar klassificeraren SVM.
    """
    # skapar SVM klassifierare
    # fyra typer av kernels som kan användas "linear", "poly", "sigmoid", "precomputed","rbf" som är default kernel om inget anges.
    # C justeras manuellt
    svm_classifier = svm.SVC(kernel="linear", gamma="auto", C=1, decision_function_shape='ovo')
    # Söker efter de optimala parameterna till SVM
    gridS = GridSearchCV(svm_classifier, param, cv=4)
    gridS.fit(feature_values, labels)
    svm_classifier = gridS.best_estimator_


def train_in_svm(essays: List[Dict[Feature, int]], features: List[Feature], grading_dict: Dict[str, Grade]) -> svm:
    global svm_classifier
    feature_values = create_feature_matrix(essays ,features)
    labels = np.array([grade.value for grade in grading_dict.values()])

    # Genom att flytta skapandet av SVM till egen metod undviks att hyperparameter tuning sker för varje omgång i experimentet
    if svm_classifier is None:
        tune_svm_classifier(feature_values, labels)

    machine_grading = {}
    # Använder SVM med parametrarna som hittades av grid search
    kf = KFold(n_splits=3, shuffle=False)
    for train_index, test_index in kf.split(feature_values):
        x_train, x_test = feature_values[train_index], feature_values[test_index]
        labels_train, labels_test = labels[train_index], labels[test_index]
        svm_classifier.fit(x_train, labels_train)
        predictions = svm_classifier.predict(x_test)
        index = 0
        for id in extract_essay_ids(test_index, essays):
            machine_grading[id] = Grade(predictions[index])
            index += 1
    cache_manager.cache_classifier(svm_classifier)
    return machine_grading


def predict_essay(essay: Dict[Feature, int], features: List[Feature], svm, ldac) -> tuple:
    feature_values = create_feature_matrix([essay], features)
    svm_prediction = svm.predict(feature_values)
    ldac_prediction = ldac.predict(feature_values)
    return (Grade(svm_prediction[0]), Grade(ldac_prediction[0]))


def train_in_ldac(essays: List[Dict[Feature, int]], features: List[Feature], grading_dict: Dict[str, Grade]):
    feature_values = create_feature_matrix(essays, features)
    labels = np.array([grade.value for grade in grading_dict.values()])
    ldac_classifier = LinearDiscriminantAnalysis()
    ldac_classifier.fit(feature_values, labels)
    machine_grading = {}
    kf = KFold(n_splits=4, shuffle=False)
    for train_index, test_index in kf.split(feature_values):
        x_train, x_test = feature_values[train_index], feature_values[test_index]
        labels_train, labels_test = labels[train_index], labels[test_index]
        ldac_classifier.fit(x_train, labels_train)
        predictions = ldac_classifier.predict(x_test)
        index = 0
        for id in extract_essay_ids(test_index, essays):
            machine_grading[id] = Grade(predictions[index])
            index += 1
    cache_manager.cache_classifier(ldac_classifier, filename="LDAC_model.pickle")
    return machine_grading
