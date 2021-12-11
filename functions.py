from paths import *
from hash import *
import datetime, jdatetime
from os.path import isfile
from uuid import getnode as get_mac
import random
import pickle
import os



def win_set_time(time_tuple):
    import win32api
    dayOfWeek = datetime.datetime(*time_tuple).isocalendar()[2]
    t = time_tuple[:2] + (dayOfWeek,) + time_tuple[2:]
    win32api.SetSystemTime(*t)


def linux_set_time(time_tuple):
    import subprocess
    import shlex

    time_string = datetime.datetime(*time_tuple).isoformat()

    subprocess.call(shlex.split("timedatectl set-ntp false")) 
    subprocess.call(shlex.split("sudo date -s '%s'" % time_string))
    subprocess.call(shlex.split("sudo hwclock -w"))


def get_grpbox_widget(grpbox, widget):
    return (w for w in grpbox.children() if isinstance(w, widget))

def layout_widgets(layout):
    return (layout.itemAt(i).widget() for i in range(layout.count())) 

def get_layout_widget(layout, widget):
    return (layout.itemAt(i).widget() for i in range(layout.count()) if isinstance(layout.itemAt(i).widget(), widget)) 


def getDiff(date):
    today = jdatetime.datetime.today().togregorian()
    nextSessionDate = date.togregorian()
    return (nextSessionDate - today).days + 1

def addExtenstion(file):
    files = os.listdir(TUTORIALS_DIR)
    if isfile(join(TUTORIALS_DIR, '.gitignore')):
        files.remove('.gitignore')
    for f in files:
        path = os.path.join(TUTORIALS_DIR, f)
        if file == Path(path).stem:
            return file + Path(path).suffix

def loadConfigs():
    configs = {}
    file = open(CONFIG_FILE, 'r')
    content = file.read().split('\n')

    for item in content:
        x = [i.strip() for i in item.split('=')]
        if len(x) > 1:
            configs[x[0]] = x[1]

    file.close()
    return configs


def randBinNumber(n):
    number = ""
    for _ in range(n):         
        temp = str(random.randint(0, 1))
        number += temp
    return number


def loadLIC():
    if not isfile(LIC):
        exit(1)

    file = open(LIC, 'rb')
    try:
        lic = pickle.load(file)
        return lic
    except Exception:
        file.close()
        
        UID0 = randBinNumber(32)
        UID1 = randBinNumber(32)
        UID2 = randBinNumber(32)

        LIC32 = (int(UID0, 2) ^ int(UID1, 2)) + (int(UID0, 2) ^ int(UID2, 2))
        LIC32 = bin(LIC32 & 0xFFFFFFFF)[2:].zfill(32)

        LicID = int(LIC32[:16], 2) ^ int(LIC32[16:], 2) & 0xFFFF

        LICENSE1 = (LicID - LicID % 10) + 1
        LICENSE2 = (LicID - LicID % 10) + 2
        LICENSE3 = (LicID - LicID % 10) + 3

        lic = {
            'KEY': UNLOCK_KEY[random.randrange(0, 100)],
            'LICENSE1': LICENSE1,
            'LICENSE2': LICENSE2,
            'LICENSE3': LICENSE3,
            'LOCK_COUNTER': 1
        }

        file = open(LIC, 'wb')
        pickle.dump(lic, file)
        file.close()
        return lic


def saveLIC(lic):
    file = open(LIC, 'wb')
    pickle.dump(lic, file)
    file.close()


def saveConfigs(configs):
    file = open(CONFIG_FILE, 'w')

    for item in configs.items():
        file.write(f'{item[0]} = {item[1]}\n')

    file.close()


def getID():
    id = ''
    if isfile('/proc/cpuinfo'):
        file = open('/proc/cpuinfo')
        for line in file:
            if line.startswith('Serial'):
                id = line.split(':')[1].strip()
    else:
        id = str(get_mac())

    return id