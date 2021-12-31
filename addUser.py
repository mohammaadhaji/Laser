from genericpath import isfile
import sys, pickle, os
from user import User
from os.path import join
from paths import USERS_DIR
from utility import randID
help = """
help:   python addUser.py N  ---> adds N users.

note:   With each execution of this command, previous users will be removed.
"""
arg = sys.argv
if not len(arg) == 2:
    print(help)
else:
    if arg[1].isnumeric():
        filePath = join(USERS_DIR, 'USERS_DATA')
        if isfile(filePath):
            os.remove(filePath)
        fileHandler = open(filePath, 'wb')
        usersData = {}
        for i in range(int(arg[1])):
            num = randID(11)
            usersData[num] = User(num, randID(5))

        usersData = pickle.dump(usersData, fileHandler)
        fileHandler.close()
    else:
        print(help)
