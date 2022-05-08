import pickle
import os

from paths import CASES_DIR


MAX_ENERGY = 100
MIN_ENRGEY = 20
MAX_FREQUENCY = 10
MIN_FREQUENCY = 1
MAX_PULSE_WIDTH = 100
MIN_PULSE_WIDTH = 20

class Case:
    def __init__(self, name):
        self.name = name
        bodyParts = ['face', 'arm', 'armpit', 'body', 'bikini', 'leg']
        self.male = dict.fromkeys(bodyParts, (MIN_ENRGEY, MIN_PULSE_WIDTH, MIN_FREQUENCY))
        self.female  = dict.fromkeys(bodyParts, (MIN_ENRGEY, MIN_PULSE_WIDTH, MIN_FREQUENCY))

    def getValue(self, sex, bodyPart):
        if sex == 'male':
            return self.male[bodyPart]

        else:
            return self.female[bodyPart]

    def save(self, sex, bodyPart, values):
        try:
            if sex == 'male':
                self.male[bodyPart] = values

            else:
                self.female[bodyPart] = values

            filePath = os.path.join(CASES_DIR, self.name)
            with open(filePath, 'wb') as f:
                pickle.dump(self, f)

        except Exception as e:
            print(e)


def openCase(name):
    filePath = os.path.join(CASES_DIR, name)

    if os.path.isfile(filePath):
        with open(filePath, 'rb') as f:
            case = pickle.load(f)

        return case
    else:
        return Case(name)
