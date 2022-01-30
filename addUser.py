import sys, pickle, os
from user import User
from os.path import join, isfile
from paths import USERS_DATA
from utility import randID, toJalali
from random import randint
import datetime
help = """
help:   python addUser.py N  ---> adds N users.

note:   With each execution of this command, previous users will be removed.
"""

def randomPhone():
    range_start = 10**(11-1)
    range_end = (10**11)-1
    return str(randint(range_start, range_end))


arg = sys.argv
if not len(arg) == 2:
    print(help)
else:
    if arg[1].isnumeric():
        if isfile(USERS_DATA):
            os.remove(USERS_DATA)
        fileHandler = open(USERS_DATA, 'wb')
        usersData = {}
        bodyParts = ['face', 'arm', 'armpit', 'body', 'bikini', 'leg']
        for i in range(int(arg[1])):
            num = randomPhone()
            x = User(num, randID(5))
            for s in range(randint(0, 10)):
                for _ in range(len(bodyParts)):
                    for shot in range(randint(0, 200)):
                        x.incShot(bodyParts[randint(0, 5)])

                x.addSession()
                x.setNextSession(
                    datetime.datetime.now() + 
                    datetime.timedelta(days=randint(1, 10))
                )
            usersData[num] = x
            print('Adding User:', i + 1, f'/ ' + arg[1], end='\r')

        usersData = pickle.dump(usersData, fileHandler)
        fileHandler.close()
    else:
        print(help)
