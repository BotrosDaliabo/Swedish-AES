from typing import Dict
from internaltypes import GradingDict, Grade

# Beräknar andelen uppsatser som tilldelats samma betyg av både lärare och datorn
def __calculate_agreement(teacher: Dict[str, Grade], machine: Dict[str, Grade]):
    assert len(teacher) == len(machine), "The number of grades does not match"
    total = len(teacher)
    agreements = 0
    for key in teacher.keys():
        if (teacher[key] == machine[key]):
            agreements += 1
    return agreements / total


# Tar emot en dictionary innehållandes ett betyg per uppsats och returnerar en dictionary innehållandes info om hur många uppsatser
# fått visst betyg, t.ex. 10 uppsatser har fått betyget G
def create_grading_dict(grades: Dict):
    grading_dict = GradingDict()
    for grade in grades.values():
        if grade == Grade.IG:
            grading_dict[Grade.IG] += 1
        elif grade == Grade.G:
            grading_dict[Grade.G] += 1
        else:
            grading_dict[Grade.VG] += 1
    return grading_dict

# Tar emot en dictionary innehållandes ett betyg för uppsats för både lärare och för maskin, en dict per var.
def calculate_kappa(teacher: Dict[str, Grade], machine: Dict[str, Grade]):
    agreement_degree = __calculate_agreement(teacher, machine)
    teacher_grades = create_grading_dict(teacher)
    machine_grades = create_grading_dict(machine)
    random_agreement = count_random_agreement(teacher_grades, machine_grades)
    return (agreement_degree - random_agreement) / (1 - random_agreement)


def count_random_agreement(teacher: GradingDict, machine: GradingDict):
    num_of_essays = teacher[Grade.IG] + teacher[Grade.G] + teacher[Grade.VG]
    assert (num_of_essays == machine[Grade.IG] + machine[Grade.G] + machine[Grade.VG])
    return (((teacher[Grade.IG] * machine[Grade.IG]) / num_of_essays) + (
            (teacher[Grade.G] * machine[Grade.G]) / num_of_essays)
            + ((teacher[Grade.VG] * machine[Grade.VG]) / num_of_essays)) / num_of_essays
