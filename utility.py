from uuid import getnode as get_mac
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from paths import *
from os.path import isfile, isdir, expanduser
import datetime, jdatetime
import subprocess, platform, pickle, hashlib
import random, uuid, os, json, shutil



def log(title, info):
    time = str(jdatetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]'))
    time += ' <' + title + '>\n'
    try:
        if not isfile(LOGS_PATH):
            open(LOGS_PATH, 'w').close()
            EncryptDecrypt(LOGS_PATH, 15)
            
        EncryptDecrypt(LOGS_PATH, 15)
        with open(LOGS_PATH, 'a') as f:
            f.write(time + info + '\n')
            
        EncryptDecrypt(LOGS_PATH, 15)
    except Exception as e:
        print(e)


RPI_MODEL = ''
RPI_VERSION = ''
if isfile('/proc/device-tree/model'):
    file = open('/proc/device-tree/model', 'r')
    RPI_MODEL = file.read()
    RPI_VERSION = RPI_MODEL.split('Pi')[1][:2].strip()
    file.close()

else:
    RPI_MODEL = 'Unknown'


OS_SPEC = ''
if platform.system() == 'Windows':
    OS_SPEC = platform.platform()
        
else:
    OS_SPEC = platform.platform().split('-with')[0].replace('-', ' ')

def monitorInfo():
    info = ''
    screen =  QtWidgets.QApplication.primaryScreen() 
    resolution = f'{screen.size().width()}x{screen.size().height()}'
    if platform.system() == 'Windows':
        # proc = subprocess.Popen(
        #     ['powershell', 'Get-WmiObject win32_desktopmonitor;'], 
        #     stdout=subprocess.PIPE
        # )
        # res = proc.communicate()
        # monitors = re.findall(
        #     '(?s)\r\nName\s+:\s(.*?)\r\n', 
        #     res[0].decode("utf-8")
        # )
        info = 'Unknown'

    else:
        subprocess.call(f'chmod 755 {MONITOR_COMMAND}', shell=True)
        subprocess.call(f'{MONITOR_COMMAND}')
        with open(MONITOR_INFO_FILE, 'r') as f:
            for l in f:
                if l.startswith('Display Product Name'):
                    info = l.split(':')[1].strip()

    return info + ' ' + resolution



def isFarsi(text):
    farsi = list('اآبپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی')
    for i in farsi:
        if i in text:
            return True

    return False

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


def EncryptDecrypt(filename, key):
    try: 
        with open(filename, 'rb') as f:
            data = f.read()
        
        data = bytearray(data)
        for index, value in enumerate(data):
            data[index] = value ^ key
            
        with open(filename, 'wb') as f:
            f.write(data)
    except Exception as e:
        log('Function: EncryptDecrypt()', str(e) + '\n')
    

def loadConfigs():
    if not isfile(CONFIG_FILE):
        print("Config file not found.")
        exit(1)
    
    try:
        EncryptDecrypt(CONFIG_FILE, 15)
        file = open(CONFIG_FILE, 'rb')
        configs = pickle.load(file)
        if len(configs) == 0:
            file.close()
            file = open(CONFIG_FILE, 'wb')
            configs['LICENSE'] = genLicense()
            configs['PASSWORD'] = ''
            configs['LANGUAGE'] = 'en'
            configs['slideTransition'] = True
            configs['touchSound'] = True
            configs['MusicVolume'] = 100
            configs['VideoVolume'] = 100
            configs['LoopMusic'] = True
            configs['theme'] = 'C1'
            configs['OwnerInfo'] = ''
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
        
        else:
            file.close()

        EncryptDecrypt(CONFIG_FILE, 15)

        return configs

    except Exception as e:
        print(e)
        exit(1)


def saveConfigs(configs):
    try:
        with open(CONFIG_FILE, 'wb') as f:
            pickle.dump(configs, f)

        EncryptDecrypt(CONFIG_FILE, 15)
        return True
    
    except Exception as e:
        print('Error in saving config file.')
        print(e)
        return False


def getID():
    id = ''
    if not RPI_MODEL == 'Unknown':
        try:
            f = open('/proc/cpuinfo','r')
            for line in f:
                if line.startswith('Serial'):
                    id = line.split(':')[1].strip()
            f.close()
        except:
            id = str(get_mac()).upper()
    
    else:
        id = str(get_mac()).upper()

    return id.upper()


def calcMD5(directory, verifyFileName):
    sumMd5 = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if Path(file_path).name == verifyFileName:
                continue
            with open(file_path, 'rb') as f:
                data = f.read()
            sumMd5 += int(hashlib.md5(data).hexdigest(), 16)
            
    return sumMd5


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


def formatTime(s):
    hours, remainder = divmod(s, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


def toJalali(date):
    if date:
        y = date.year
        m = date.month
        d = date.day
        return jdatetime.datetime.fromgregorian(year=y, month=m, day=d)



def calcPosition(pos):
    seconds = int((pos/1000) % 60)
    minutes = int((pos/60000) % 60)
    hours = int((pos/3600000) % 24)
    return hours, minutes, seconds


MOUNT_DIR = '/media/musics'
def musicCleanup(mountPoint):
    try:
        for mp in mountPoint.values():
            os.system(f'umount {mp}')
        if isdir(MOUNT_DIR):
            shutil.rmtree(MOUNT_DIR)
    except Exception as e:
        log('Read Music', str(e) + '\n')


class ReadMusics(QThread):
    result = pyqtSignal(str)
    paths = pyqtSignal(list)
    def __init__(self):
        super(QThread, self).__init__()
        self.auto = True

    def setAuto(self, i):
        self.auto = i

    def run(self):
        try:
            if platform.system() == 'Windows':
                self.result.emit("Not in windows.")
                return
                            
            r1  = subprocess.check_output('lsblk -J', shell=True)
            blocks = json.loads(r1)['blockdevices']

            sdaFound = False
            sdaBlock = None
            for blk in blocks:
                if blk['name'].startswith('sd'):
                    sdaFound = True
                    sdaBlock = blk

            if not sdaFound:
                err = "Flash drive not found."
                self.result.emit(err)
                log('Read Music', err + '\n')
                return
                    
            if not 'children' in sdaBlock:
                err = "Flash drive doesn't have any partitions."
                self.result.emit(err)
                log('Read Music', err + '\n')
                return
            

            MOUNT_DIR = '/media/musics'
            if not isdir(MOUNT_DIR):
                os.mkdir(MOUNT_DIR)

            partitionsDir = {}
            for part in sdaBlock['children']:
                partitionsDir[part['name']] = part['mountpoint']

            for part in partitionsDir:
                if partitionsDir[part] == None:
                    if not isdir(f'{MOUNT_DIR}/{part}'):
                        os.mkdir(f'{MOUNT_DIR}/{part}')
                    r = subprocess.call(
                        f'mount /dev/{part} {MOUNT_DIR}/{part}',
                        shell=True
                    )
                    partitionsDir[part] = f'{MOUNT_DIR}/{part}'

            musicFiles = []
            for dir in partitionsDir.values():
                for r,d,f in os.walk(dir):
                    for file in f:
                        fPath = os.path.join(r, file)
                        name, extension = os.path.splitext(fPath)
                        if extension in ['.mp3', '.wav']:
                            musicFiles.append(fPath)


            if len(musicFiles) == 0:
                self.result.emit('No music found.')
                musicCleanup(partitionsDir)
                return

            self.paths.emit(musicFiles)
        
        except Exception as e:
            self.result.emit(str(e))
            log('Read Music, Unhandled Exception', str(e) + '\n')
            musicCleanup(partitionsDir)
