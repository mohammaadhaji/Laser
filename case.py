from paths import CASES_DIR
from os.path import join, isfile
import pickle

MAX_ENERGY = 200
MIN_ENRGEY = 3
MAX_FREQUENCY = 10
MIN_FREQUENCY = 1
MAX_PULSE_WIDTH = 200
MIN_PULSE_WIDTH = 3

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

            filePath = join(CASES_DIR, self.name)
            fileHandler = open(filePath, 'wb')
            pickle.dump(self, fileHandler)
            fileHandler.close()
        except Exception as e:
            print(e)

def openCase(name):
    filePath = join(CASES_DIR, name)
    if isfile(filePath):
        fileHandler = open(filePath, 'rb')
        case = pickle.load(fileHandler)
        fileHandler.close()
        return case
    else:
        return Case(name)
