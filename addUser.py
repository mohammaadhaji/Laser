import sys, pickle, os
from user import User
from os.path import join, isfile
from paths import USERS_DATA
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
        if isfile(USERS_DATA):
            os.remove(USERS_DATA)
        fileHandler = open(USERS_DATA, 'wb')
        usersData = {}
        for i in range(int(arg[1])):
            num = randID(11)
            x = User(num, randID(5))
            x.addSession()
            usersData[num] = x

        usersData = pickle.dump(usersData, fileHandler)
        fileHandler.close()
    else:
        print(help)
