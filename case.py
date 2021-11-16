from paths import CASES_DIR
from os.path import join, isfile
import pickle


class Case:
    def __init__(self, name):
        self.name = name
        bodyParts = ['face', 'arm', 'armpit', 'body', 'bikini', 'leg']
        self.male = dict.fromkeys(bodyParts, (0, 0, 0))
        self.female  = dict.fromkeys(bodyParts, (0, 0, 0))

    def getValue(self, sex, bodyPart):
        if sex == 'male':
            return self.male[bodyPart]

        else:
            return self.female[bodyPart]

    def save(self, sex, bodyPart, values):
        if sex == 'male':
            self.male[bodyPart] = values

        else:
            self.female[bodyPart] = values

        filePath = join(CASES_DIR, self.name)
        fileHandler = open(filePath, 'wb')
        pickle.dump(self, fileHandler)
        fileHandler.close()
        

def openCase(name):
    filePath = join(CASES_DIR, name)
    if isfile(filePath):
        fileHandler = open(filePath, 'rb')
        case = pickle.load(fileHandler)
        fileHandler.close()
        return case
    else:
        return Case(name)
