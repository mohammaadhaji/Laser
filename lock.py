from itertools import count
from paths import LOCK_DIR
from functions import getDiff, loadLIC
from os.path import join, isfile
import pickle
import os


class Lock:
    def __init__(self, date, license=1):
        self.name = 'dll' + str(len(os.listdir(LOCK_DIR)))
        self.date = date
        self.paid = False
        self.license = license
        self.unlockPass = [None ,0xABCD, 0xBCDE, 0xCDEF][int(str(license)[-1])]
        self.save()

    def getStatus(self):
        return getDiff(self.date)

    def setPaid(self, paid):
        self.paid = paid

    def checkPassword(self, password):
        if password ^ self.license == self.unlockPass:
            self.paid = True
            self.save()

        return self.paid

    def save(self):
        filePath = join(LOCK_DIR, self.name)
        fileHandler = open(filePath, 'wb')
        pickle.dump(self, fileHandler)
        fileHandler.close()


def countLocks():
    locks = os.listdir(LOCK_DIR)
    if isfile(join(LOCK_DIR, '.gitignore')):
        locks.remove('.gitignore')

    return len(locks)

def loadLock(name):
    filePath = join(LOCK_DIR, name)
    if isfile(filePath):
        fileHandler = open(filePath, 'rb')
        lcok = pickle.load(fileHandler)
        fileHandler.close()
        return lcok


def loadLocks():
    locks = os.listdir(LOCK_DIR)
    if isfile(join(LOCK_DIR, '.gitignore')):
        locks.remove('.gitignore')
    loadedLocks = []
    for name in locks:
        lock = loadLock(name)
        if not lock.paid and lock.getStatus() <= 0:
            loadedLocks.append(lock)

    loadedLocks.sort(key=lambda x: x.date)
    return loadedLocks


def loadAllLocks():
    locks = os.listdir(LOCK_DIR)
    if isfile(join(LOCK_DIR, '.gitignore')):
        locks.remove('.gitignore')

    loadedLocks = []
    for name in locks:
        lock = loadLock(name)
        loadedLocks.append(lock)

    loadedLocks.sort(key=lambda x: x.date)
    return loadedLocks

def anyLockBefor(date):
    locks = loadAllLocks()

    for lock in locks:
        if (date - lock.date).days <= 0:
            return True
    
    return False


def removeLock(date):
    locks = loadAllLocks()

    for lock in locks:
        if (date - lock.date).days == 0:
            os.remove(join(LOCK_DIR, lock.name))
