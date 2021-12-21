from uuid import getnode as get_mac

from PyQt5.QtCore import QThread, pyqtSignal
from paths import *
from os.path import isfile, isdir
import datetime, jdatetime
import subprocess, platform, pickle
import random, uuid, os, re, json, shutil


def setSystemTime(time):
    if platform.system() == 'Windows':
        import win32api
        time_string = f'{time[0]} {time[1]} {time[2]} {time[3]} {time[4]} {time[5]} {time[6]}'
        datetime_obj = datetime.datetime.strptime(time_string, '%Y %m %d %H %M %S %f') 
        utc_datetime = datetime_obj.astimezone().astimezone(datetime.timezone.utc).replace(tzinfo=None)
        day_of_week = utc_datetime.isocalendar()[2]
        win32api.SetSystemTime(utc_datetime.year, utc_datetime.month, day_of_week, 
        utc_datetime.day, utc_datetime.hour, utc_datetime.minute, utc_datetime.second,
        int(utc_datetime.microsecond / 1000))
    
    else:
        import subprocess
        import shlex
        time_string = datetime.datetime(*time).isoformat()
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


def randBinNumber(n):
    number = ""
    for _ in range(n):         
        temp = str(random.randint(0, 1))
        number += temp
    return number


def randID(string_length=5):
    random = str(uuid.uuid4())
    random = random.upper() 
    random = random.replace("-","")
    return random[0:string_length]


def genLicense():   
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
        'LICENSE1': LICENSE1,
        'LICENSE2': LICENSE2,
        'LICENSE3': LICENSE3,
    }
    return lic


def loadConfigs():
    if not isfile(CONFIG_FILE):
        print("Don't be an asshole")
        exit(1)
    
    file = open(CONFIG_FILE, 'rb')
    try:
        configs = pickle.load(file)
        if len(configs) == 0:
            file.close()
            file = open(CONFIG_FILE, 'wb')
            configs['LICENSE'] = genLicense()
            configs['PASSWORD'] = ''
            configs['LANGUAGE'] = 'en'
            configs['SerialNumber'] = ''
            configs['TotalShotCounter'] = 0
            configs['LaserDiodeEnergy'] = ''
            configs['LaserBarType'] = ''
            configs['LaserWavelength'] = ''
            configs['DriverVersion'] = ''
            configs['MainControlVersion'] = ''
            configs['FirmwareVersion'] = ''
            configs['ProductionDate'] = ''
            configs['GuiVersion'] = 'v1.0'
            configs['LOCK'] = []
            pickle.dump(configs, file)
            file.close()

        return configs

    except Exception:
        print("Don't be an asshole")
        exit(1)


def saveConfigs(configs):
    file = open(CONFIG_FILE, 'wb')
    pickle.dump(configs, file)
    file.close()


def getID():
    id = ''
    if platform.system() == 'Linux':
        r = subprocess.check_output('blkid -s UUID -o value', shell=True)
        r = re.sub('[^a-zA-Z0-9]', '', str(r)).upper()
        if len(r) >= 10:
            id = r[:10]
        else:
            id = r
    
    else:
        r = str(get_mac()).upper()
        if len(r) >= 10:
            id = r[:10]
        else:
            id = r

    return id


class UpdateFirmware(QThread):
    result = pyqtSignal(str)
    
    def __init__(self, parent):
        super().__init__(parent=parent)

    def run(self):
        if platform.system() == 'Windows':
            self.result.emit("We don't do that here.")
                            
        r1  = subprocess.check_output('lsblk -J', shell=True)
        blocks = json.loads(r1)['blockdevices']

        sdaFound = False
        sdaBlock = None
        for blk in blocks:
            if blk['name'] == 'sda':
                sdaFound = True
                sdaBlock = blk

        if not sdaFound:
            self.result.emit("Flash Drive not found.")
                
        if not 'children' in sdaBlock:
            self.result.emit("Flash drive doesn't have any partitions.")
            
        mountDir ='/media/updateFirmware' 
        os.mkdir(mountDir)
        partitionsDir = {}

        for part in sdaBlock['children']:
            partitionsDir[part['name']] = part['mountpoint']

        for part in partitionsDir:
            if partitionsDir[part] == None:
                    os.mkdir(f'{mountDir}/{part}')
                    r = subprocess.call(
                        f'mount /dev/{part} {mountDir}/{part}',
                        shell=True
                    )
                    partitionsDir[part] = f'{mountDir}/{part}'

        laserFound = False
        laserDir = ''
        for dir in partitionsDir.values():
            if isdir(f'{dir}/Laser'):
                laserFound = True
                laserDir = f'{dir}/Laser'

        if not laserFound:
            self.result.emit("Source files not found.")
            
        os.system(f'cp -r {laserDir}/* {CURRENT_FILE_DIR}')
        os.system(f'umount {mountDir}/sda*')
        shutil.rmtree(mountDir)
        self.result.emit("Done")