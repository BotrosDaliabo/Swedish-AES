# Skriptet används enbart i felsökningssyfte
from typing import List, Dict
from internaltypes import Feature, Grade, GradingDict

def __create_grading_dict(grades: Dict):
    grading_dict = GradingDict()
    for grade in grades.values():
        if grade == Grade.IG:
            grading_dict[Grade.IG] += 1
        elif grade == Grade.G:
            grading_dict[Grade.G] += 1
        else:
            grading_dict[Grade.VG] += 1
    return grading_dict


def cache_ess1ays(essays: List[Dict[Feature, int]]):
    import pickle
    pickle.dump(essays, open("essays.pickle", "wb"))

def read_essays() -> List[Dict[Feature, int]]:
    import pickle
    return pickle.load(open("essays.pickle", "rb"))


if __name__ == '__main__':
    pass
