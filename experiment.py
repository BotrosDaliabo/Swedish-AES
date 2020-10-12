import itertools
from multiprocessing.pool import ThreadPool
from typing import List, Dict

from natsort import natsorted

import cache_manager
from evaluate import calculate_kappa
from internaltypes import Feature, Grade
from predict import train_in_svm, train_in_ldac

essay_collection: List[Dict[Feature, int]]
grade_dict: Dict[str, Grade]

def start_experiment(teacher_grades: Dict, essays: List[Dict]):
    global essay_collection, grade_dict
    grade_dict = teacher_grades
    essay_collection = essays
    SVM_kappas: List[(List, float)] = []
    LDAC_kappas: List[(List, float)] = []
    features = Feature.__members__.values()
    features_list: List[Feature] = list(features)
    data = itertools.chain.from_iterable(itertools.combinations(features_list, r) for r in range(1, len(features_list)+1))
    feature_sets = list(data)
    thread_pool = ThreadPool(processes=1)
    async_result = thread_pool.apply_async(__feature_classification_LDAC, args=[feature_sets])
    print("Starting the experiment")
    SVM_kappas = __feature_classification_SVM(feature_sets)
    LDAC_kappas = async_result.get()
    cache_manager.cache_features_kappas(SVM_kappas, LDAC_kappas)


def __feature_classification_SVM(feature_sets) -> List:
    kappas: List[(List, float)] = []
    for features in feature_sets:
        features_list = list(features)
        SVM_grades = (train_in_svm(essay_collection, features_list, grade_dict))
        kappas.append((features_list, calculate_kappa(grade_dict, SVM_grades)))

    return kappas


def __feature_classification_LDAC(feature_sets) -> List:
    kappas: List[(List, float)] = []
    for features in feature_sets:
        features_list = list(features)
        LDAC_grades = train_in_ldac(essay_collection, features_list, grade_dict)
        kappas.append((features_list, calculate_kappa(grade_dict, LDAC_grades)))

    return kappas


def get_results(count: int) -> tuple:
    """
    Returnerar det antal av toppresultaten som specificeras av parameter.
    :param count: Antalet resultat från SVM-experimentet och LDAC-experimentet, alltså kappavärden.
    :return: En tuple där första värde är en lista med resultat från SVM (kappavärden), den andra är en lista med resultat från LDAC (kappavärden)
    """
    SVM_kappas = cache_manager.read_feature_kappas()
    LDAC_kappas = cache_manager.read_feature_kappas("LDAC_features_kappas.pickle")
    SVM_kappas_sorted = natsorted(seq=SVM_kappas, reverse=True, key=lambda tup: tup[1])
    LDAC_kappas_sorted = natsorted(seq=LDAC_kappas, reverse=True, key=lambda tup: tup[1])
    result: tuple = ([],[])
    for index in range(0, count):
        for index2 in range(len(SVM_kappas_sorted[index][0])):
            SVM_kappas_sorted[index][0][index2] = SVM_kappas_sorted[index][0][index2].name
        for index2 in range(len(LDAC_kappas_sorted[index][0])):
            LDAC_kappas_sorted[index][0][index2] = LDAC_kappas_sorted[index][0][index2].name
        result[0].append(SVM_kappas_sorted[index])
        result[1].append(LDAC_kappas_sorted[index])

    return result


def get_feature_count(results: tuple) -> tuple:
    feature_dict_SVM = {}
    feature_dict_LDAC = {}
    for feature in Feature.__members__.values():
        feature_dict_SVM[feature.name] = 0
        feature_dict_LDAC[feature.name] = 0

    for tuple in results[0]:
        for feature in tuple[0]:
            feature_dict_SVM[feature] += 1

    for tuple in results[1]:
        for feature in tuple[0]:
            feature_dict_LDAC[feature] += 1

    return (feature_dict_SVM, feature_dict_LDAC)