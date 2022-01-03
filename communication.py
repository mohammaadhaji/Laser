from PyQt5.QtCore import QObject, QThread, pyqtSignal
from crccheck.crc import Crc16Xmodem
from serial import Serial
import jdatetime, platform 
from utility import *
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
    chan_list = [12,16]
    GPIO.setup(chan_list, GPIO.OUT)
    GPIO.output(chan_list, GPIO.HIGH)
except Exception:
    pass

def gpioCleanup():
    try:
        GPIO.cleanup()
    except Exception:
        pass

if platform.system() == 'Windows':
    serial = Serial('COM2', 115200)
else:
    serial = Serial('/dev/ttyS0', 115200)

HEADER_1   = 1
HEADER_2   = 2
CHECK_NOB  = 3
IN_MESSAGE = 4
STATE      = HEADER_1

PAGE_INDEX     = 1
FIELD_INDEX    = 2
CMD_TYPE_INDEX = 3

LASER_PAGE     = 0
SETTING_PAGE   = 1
LOCK_TIME_PAGE = 2
BODY_PART_PAGE = 3
MAIN_PAGE      = 4
SHUTDONW_PAGE  = 5
UPDATE_PAGE    = 6

REPORT = 0x0A
WRITE  = 0x0B 
READ   = 0x0C


MOUNT_DIR        ='/media/updateFirmware'
SOURCE_FOLDER    = 'Laser'
MICRO_SOURCE     = 'Application_v1.0.bin'
MICRO_DATA       = {}
PACKET_NOB       = 1000


RECEIVED_DATA = bytearray()


def printPacket(packet):
    print( " ".join(packet.hex()[i:i+2].upper() for i in range(0, len(packet.hex()), 2)))


def sensors(packet):
    flags = [False] * 5

    if packet[4]:
        flags[0] = False
    else:
        flags[0] = True

    if packet[5]:
        flags[1] = False
    else:
        flags[1] = True

    if packet[6]:
        flags[2] = False
    else:
        flags[2] = True

    if packet[7]:
        flags[3] = False
    else:
        flags[3] = True

    if packet[8]:
        flags[4] = False
    else:
        flags[4] = True

    return flags


def buildPacket(data, page, field, cmdType):
    packet = bytearray()
    packet.append(0xAA)
    packet.append(0xBB)
    packet.append(5 + len(data))
    packet.append(page)
    packet.append(field)
    packet.append(cmdType)
    packet += data
    crc = Crc16Xmodem.calc(packet[2:])
    crc_bytes = crc.to_bytes(2, byteorder='big')
    packet += crc_bytes
    packet.append(0xCC)
    return packet


def sendPacket(fieldsIndex, fieldValues, page, cmdType=REPORT):
    
    for field, value in fieldValues.items():
        packet = buildPacket(str(value).encode(), page, fieldsIndex[field], cmdType)
        serial.write(packet)


def enterPage(page):
    packet = bytearray(9)
    packet[0] = 0xAA
    packet[1] = 0xBB
    packet[2] = 0x05 
    packet[3] = page 
    packet[4] = 0xAA 
    packet[5] = REPORT  
    crc = Crc16Xmodem.calc(packet[2:-3])
    crc_bytes = crc.to_bytes(2, byteorder='big')
    packet[6] = crc_bytes[0]
    packet[7] = crc_bytes[1]
    packet[8] = 0xCC
    serial.write(packet)


def readTime():
    packet = bytearray(9)
    packet[0] = 0xAA
    packet[1] = 0xBB
    packet[2] = 0x05 
    packet[3] = LOCK_TIME_PAGE 
    packet[4] = 0x01 
    packet[5] = READ  
    crc = Crc16Xmodem.calc(packet[2:-3])
    crc_bytes = crc.to_bytes(2, byteorder='big')
    packet[6] = crc_bytes[0]
    packet[7] = crc_bytes[1]
    packet[8] = 0xCC
    serial.write(packet)
    packet[4] = 0x00
    crc = Crc16Xmodem.calc(packet[2:-3])
    crc_bytes = crc.to_bytes(2, byteorder='big')
    packet[6] = crc_bytes[0]
    packet[7] = crc_bytes[1]
    serial.write(packet)


def laserPage(fieldValues):
    fieldsIndex = {
        'cooling': 3 , 'energy': 4, 'pulseWidth': 5,
        'frequency':6, 'couter': 7, 'ready-standby': 8
    }
    sendPacket(fieldsIndex, fieldValues, LASER_PAGE)


def settingsPage(fieldValues, cmdType):
    fieldsIndex = {
        'serial': 0, 'totalCounter': 1, 'pDate': 2,
        'LaserEnergy': 3, 'waveLength': 4, 'LaserBarType': 5,
        'DriverVersion': 6, 'controlVersion': 7, 'firmware': 8,
        'monitor': 9, 'os': 10, 'gui': 11, 'rpi': 12
    }
    sendPacket(fieldsIndex, fieldValues, SETTING_PAGE, cmdType)


def lockPage(cmdType):
    fieldsIndex = { 'clock': 0, 'date': 1}
    clock = jdatetime.datetime.now().strftime('%H : %M : %S')
    date  = jdatetime.datetime.now().togregorian().strftime('%Y-%m-%d')
    fieldValues = {'clock': clock, 'date': date}
    sendPacket(fieldsIndex, fieldValues, LOCK_TIME_PAGE, cmdType)


class SerialTimer(QObject):
    sensorFlags = pyqtSignal(list)
    tempValue = pyqtSignal(int)
    shot = pyqtSignal()
    serialNumber = pyqtSignal(str)
    productionDate = pyqtSignal(str)
    laserEnergy = pyqtSignal(str)
    firmwareVesion = pyqtSignal(str)
    readCooling = pyqtSignal()
    readEnergy = pyqtSignal()
    readPulseWidht = pyqtSignal()
    readFrequency = pyqtSignal()
    sysClock = pyqtSignal(tuple)
    sysDate = pyqtSignal(tuple)
    updateProgress = pyqtSignal(str)

    def __init__(self):
        super(QObject, self).__init__()


    def closePort(self):
        serial.close()

    def checkBuffer(self):
        if serial.is_open and serial.in_waiting > 1:
            self.readDate()

    def readDate(self):
        global STATE, RECEIVED_DATA
        nob = 0

        try:
            temp = serial.read_all()
            counter = 0

            if temp:
                len_temp = len(temp)
                while counter < len_temp:
                    if STATE == HEADER_1:

                        if temp[counter] == 0xAA:
                            STATE = HEADER_2

                    elif STATE == HEADER_2:

                        if temp[counter] == 0xBB:
                            STATE = CHECK_NOB
                            RECEIVED_DATA[:] = []

                    elif STATE == CHECK_NOB:
                        nob = temp[counter]
                        STATE = IN_MESSAGE

                    elif STATE == IN_MESSAGE:
                    
                        if len(RECEIVED_DATA) == nob:
                            STATE = HEADER_1
                            RECEIVED_DATA[0:0] = nob.to_bytes(
                                length=1, 
                                byteorder='big'
                            )

                            crc_s = int.from_bytes(
                                RECEIVED_DATA[-2:], 
                                byteorder='big', 
                                signed=False
                            )

                            crc_r = Crc16Xmodem.calc(
                                RECEIVED_DATA[:-2]
                            )
                            
                            if crc_r == crc_s:
                                if RECEIVED_DATA[CMD_TYPE_INDEX] == REPORT:
                                    
                                    if RECEIVED_DATA[PAGE_INDEX] == SETTING_PAGE:
                                        if RECEIVED_DATA[FIELD_INDEX] == 0:
                                            serNum = RECEIVED_DATA[4:-2].decode()
                                            d = serNum[-2:]
                                            m = serNum[-4:-2]
                                            y = serNum[-8:-4]
                                            pdate = y + ' / ' + m + ' / ' + d
                                            self.productionDate.emit(pdate)
                                            self.serialNumber.emit(serNum)

                                        elif RECEIVED_DATA[FIELD_INDEX] == 3:
                                            lEnergy = RECEIVED_DATA[4:-2].decode()
                                            self.laserEnergy.emit(lEnergy)

                                        elif RECEIVED_DATA[FIELD_INDEX] == 8:
                                            firmware = RECEIVED_DATA[4:-2].decode()
                                            self.firmwareVesion.emit(firmware)

                                    elif RECEIVED_DATA[PAGE_INDEX] == LOCK_TIME_PAGE:
                                        if RECEIVED_DATA[FIELD_INDEX] == 0:
                                            clock = RECEIVED_DATA[4:-2].decode()
                                            clock = clock.split(':')
                                            clock = tuple( int(x) for x in clock )
                                            self.sysClock.emit(clock)
                                        elif RECEIVED_DATA[FIELD_INDEX] == 1:
                                            date = RECEIVED_DATA[4:-2].decode()
                                            date = date.split('-')
                                            date = tuple( int(x) for x in date )
                                            self.sysDate.emit(date)
                                    elif RECEIVED_DATA[PAGE_INDEX] == UPDATE_PAGE:
                                        if RECEIVED_DATA[FIELD_INDEX] == 252:
                                            status = RECEIVED_DATA[4:-2].decode()
                                            self.updateProgress.emit(status)


                                elif RECEIVED_DATA[CMD_TYPE_INDEX] == WRITE:

                                    if RECEIVED_DATA[PAGE_INDEX] in (LASER_PAGE, BODY_PART_PAGE):
                                        if RECEIVED_DATA[FIELD_INDEX] == 0:     
                                            flags = sensors(RECEIVED_DATA)
                                            self.sensorFlags.emit(flags)

                                        if RECEIVED_DATA[FIELD_INDEX] == 1:
                                            t = RECEIVED_DATA[4:-2].decode()
                                            self.tempValue.emit(int(t))

                                        if RECEIVED_DATA[FIELD_INDEX] == 7:
                                            shot = RECEIVED_DATA[4:-2].hex()
                                            if int(shot, 16) == 1:
                                                self.shot.emit()

                                    elif RECEIVED_DATA[PAGE_INDEX] == SETTING_PAGE:
                                        if RECEIVED_DATA[FIELD_INDEX] == 0:
                                            serNum = RECEIVED_DATA[4:-2].decode()
                                            d = serNum[-2:]
                                            m = serNum[-4:-2]
                                            y = serNum[-8:-4]
                                            pdate = y + ' / ' + m + ' / ' + d
                                            self.productionDate.emit(pdate)
                                            self.serialNumber.emit(serNum)

                                        elif RECEIVED_DATA[FIELD_INDEX] == 3:
                                            lEnergy = RECEIVED_DATA[4:-2].decode()
                                            self.laserEnergy.emit(lEnergy)

                                        elif RECEIVED_DATA[FIELD_INDEX] == 8:
                                            firmware = RECEIVED_DATA[4:-2].decode()
                                            self.firmwareVesion.emit(firmware)
                                
                                elif RECEIVED_DATA[CMD_TYPE_INDEX] == READ:
                                    if RECEIVED_DATA[PAGE_INDEX] == LASER_PAGE:

                                        if RECEIVED_DATA[FIELD_INDEX] == 3:
                                            self.readCooling.emit()
                                        elif RECEIVED_DATA[FIELD_INDEX] == 4:
                                            self.readEnergy.emit()
                                        elif RECEIVED_DATA[FIELD_INDEX] == 5:
                                            self.readPulseWidht.emit()
                                        elif RECEIVED_DATA[FIELD_INDEX] == 6:
                                            self.readFrequency.emit()

                                    elif RECEIVED_DATA[PAGE_INDEX] == UPDATE_PAGE:
                                        segmentIndex = RECEIVED_DATA[FIELD_INDEX]
                                        if segmentIndex in MICRO_DATA.keys():
                                            serial.write(
                                                MICRO_DATA[segmentIndex]
                                            )
                                        elif RECEIVED_DATA[FIELD_INDEX] == 250:
                                            serial.write(
                                                MICRO_DATA[250]
                                            )
                                        elif RECEIVED_DATA[FIELD_INDEX] == 251:
                                            serial.write(
                                                MICRO_DATA[251]
                                            )

                        else:
                            RECEIVED_DATA.append(temp[counter])

                    counter = counter + 1
        except Exception as e:
            print(e)


class SerialThread(QThread):
    sensorFlags = pyqtSignal(list)
    tempValue = pyqtSignal(int)
    shot = pyqtSignal()
    serialNumber = pyqtSignal(str)
    productionDate = pyqtSignal(str)
    laserEnergy = pyqtSignal(str)
    firmwareVesion = pyqtSignal(str)
    readCooling = pyqtSignal()
    readEnergy = pyqtSignal()
    readPulseWidht = pyqtSignal()
    readFrequency = pyqtSignal()
    sysClock = pyqtSignal(tuple)
    sysDate = pyqtSignal(tuple)
    updateProgress = pyqtSignal(str)

    def __init__(self):
        super(QThread, self).__init__()
        self.loop = True


    def closePort(self):
        self.loop = False
        serial.close()


    def run(self):
        global STATE, RECEIVED_DATA
        nob = 0
        while self.loop:
            try:
                temp = serial.read_all()
                counter = 0

                if temp:
                    len_temp = len(temp)
                    while counter < len_temp:
                        if STATE == HEADER_1:

                            if temp[counter] == 0xAA:
                                STATE = HEADER_2

                        elif STATE == HEADER_2:

                            if temp[counter] == 0xBB:
                                STATE = CHECK_NOB
                                RECEIVED_DATA[:] = []

                        elif STATE == CHECK_NOB:
                            nob = temp[counter]
                            STATE = IN_MESSAGE

                        elif STATE == IN_MESSAGE:
                        
                            if len(RECEIVED_DATA) == nob:
                                STATE = HEADER_1
                                RECEIVED_DATA[0:0] = nob.to_bytes(
                                    length=1, 
                                    byteorder='big'
                                )

                                crc_s = int.from_bytes(
                                    RECEIVED_DATA[-2:], 
                                    byteorder='big', 
                                    signed=False
                                )

                                crc_r = Crc16Xmodem.calc(
                                    RECEIVED_DATA[:-2]
                                )
                                
                                if crc_r == crc_s:
                                    if RECEIVED_DATA[CMD_TYPE_INDEX] == REPORT:
                                        
                                        if RECEIVED_DATA[PAGE_INDEX] == SETTING_PAGE:
                                            if RECEIVED_DATA[FIELD_INDEX] == 0:
                                                serNum = RECEIVED_DATA[4:-2].decode()
                                                d = serNum[-2:]
                                                m = serNum[-4:-2]
                                                y = serNum[-8:-4]
                                                pdate = y + ' / ' + m + ' / ' + d
                                                self.productionDate.emit(pdate)
                                                self.serialNumber.emit(serNum)

                                            elif RECEIVED_DATA[FIELD_INDEX] == 3:
                                                lEnergy = RECEIVED_DATA[4:-2].decode()
                                                self.laserEnergy.emit(lEnergy)

                                            elif RECEIVED_DATA[FIELD_INDEX] == 8:
                                                firmware = RECEIVED_DATA[4:-2].decode()
                                                self.firmwareVesion.emit(firmware)

                                        elif RECEIVED_DATA[PAGE_INDEX] == LOCK_TIME_PAGE:
                                            if RECEIVED_DATA[FIELD_INDEX] == 0:
                                                clock = RECEIVED_DATA[4:-2].decode()
                                                clock = clock.split(':')
                                                clock = tuple( int(x) for x in clock )
                                                self.sysClock.emit(clock)
                                            elif RECEIVED_DATA[FIELD_INDEX] == 1:
                                                date = RECEIVED_DATA[4:-2].decode()
                                                date = date.split('-')
                                                date = tuple( int(x) for x in date )
                                                self.sysDate.emit(date)
                                        
                                        elif RECEIVED_DATA[PAGE_INDEX] == UPDATE_PAGE:
                                            if RECEIVED_DATA[FIELD_INDEX] == 252:
                                                status = RECEIVED_DATA[4:-2].decode()
                                                self.updateProgress.emit(status)

                                    elif RECEIVED_DATA[CMD_TYPE_INDEX] == WRITE:

                                        if RECEIVED_DATA[PAGE_INDEX] in (LASER_PAGE, BODY_PART_PAGE):
                                            if RECEIVED_DATA[FIELD_INDEX] == 0:     
                                                flags = sensors(RECEIVED_DATA)
                                                self.sensorFlags.emit(flags)

                                            if RECEIVED_DATA[FIELD_INDEX] == 1:
                                                t = RECEIVED_DATA[4:-2].decode()
                                                self.tempValue.emit(int(t))

                                            if RECEIVED_DATA[FIELD_INDEX] == 7:
                                                shot = RECEIVED_DATA[4:-2].hex()
                                                if int(shot, 16) == 1:
                                                    self.shot.emit()

                                        elif RECEIVED_DATA[PAGE_INDEX] == SETTING_PAGE:
                                            if RECEIVED_DATA[FIELD_INDEX] == 0:
                                                serNum = RECEIVED_DATA[4:-2].decode()
                                                d = serNum[-2:]
                                                m = serNum[-4:-2]
                                                y = serNum[-8:-4]
                                                pdate = y + ' / ' + m + ' / ' + d
                                                self.productionDate.emit(pdate)
                                                self.serialNumber.emit(serNum)

                                            elif RECEIVED_DATA[FIELD_INDEX] == 3:
                                                lEnergy = RECEIVED_DATA[4:-2].decode()
                                                self.laserEnergy.emit(lEnergy)

                                            elif RECEIVED_DATA[FIELD_INDEX] == 8:
                                                firmware = RECEIVED_DATA[4:-2].decode()
                                                self.firmwareVesion.emit(firmware)
                                    
                                    elif RECEIVED_DATA[CMD_TYPE_INDEX] == READ:
                                        if RECEIVED_DATA[PAGE_INDEX] == LASER_PAGE:

                                            if RECEIVED_DATA[FIELD_INDEX] == 3:
                                                self.readCooling.emit()
                                            elif RECEIVED_DATA[FIELD_INDEX] == 4:
                                                self.readEnergy.emit()
                                            elif RECEIVED_DATA[FIELD_INDEX] == 5:
                                                self.readPulseWidht.emit()
                                            elif RECEIVED_DATA[FIELD_INDEX] == 6:
                                                self.readFrequency.emit()

                                        elif RECEIVED_DATA[PAGE_INDEX] == LASER_PAGE:
                                            segmentIndex = RECEIVED_DATA[FIELD_INDEX]
                                            if segmentIndex in MICRO_DATA.keys():
                                                serial.write(
                                                    MICRO_DATA[segmentIndex]
                                                )

                            else:
                                RECEIVED_DATA.append(temp[counter])

                        counter = counter + 1
            except Exception as e:
                print(e)


class UpdateFirmware(QThread):
    result = pyqtSignal(str)

    def run(self):
        global MICRO_DATA
        MICRO_DATA.clear()

        if platform.system() == 'Windows':
            self.result.emit("We don't do that here.")
            return

        self.msleep(20)                            
        r1  = subprocess.check_output('lsblk -J', shell=True)
        blocks = json.loads(r1)['blockdevices']

        sdaFound = False
        sdaBlock = None
        for blk in blocks:
            if blk['name'] == 'sda':
                sdaFound = True
                sdaBlock = blk

        if not sdaFound:
            self.result.emit("Flash drive not found.")
            return
                
        if not 'children' in sdaBlock:
            self.result.emit("Flash drive doesn't have any partitions.")
            return
             
        os.mkdir(MOUNT_DIR)
        partitionsDir = {}

        for part in sdaBlock['children']:
            partitionsDir[part['name']] = part['mountpoint']

        for part in partitionsDir:
            if partitionsDir[part] == None:
                os.mkdir(f'{MOUNT_DIR}/{part}')
                r = subprocess.call(
                    f'mount /dev/{part} {MOUNT_DIR}/{part}',
                    shell=True
                )
                partitionsDir[part] = f'{MOUNT_DIR}/{part}'

        laserFound = False
        laserDir = ''
        for dir in partitionsDir.values():
            if isdir(f'{dir}/{SOURCE_FOLDER}'):
                laserFound = True
                laserDir = f'{dir}/{SOURCE_FOLDER}'

        if not laserFound:
            self.result.emit("Source files not found.")
            os.system(f'umount {MOUNT_DIR}/sda*')
            shutil.rmtree(MOUNT_DIR)
            return

        verifyError = 'The source files are corrupted and can not be replaced.'
        try:
            with open(f'{laserDir}/verify', 'r') as f:
                md5 = int(f.read())

            if not md5 == calcMD5(laserDir, 'verify'):
                self.result.emit(verifyError)
                os.system(f'umount {MOUNT_DIR}/sda*')
                shutil.rmtree(MOUNT_DIR)
                return
   
        except Exception:
            self.result.emit(verifyError)
            os.system(f'umount {MOUNT_DIR}/sda*')
            shutil.rmtree(MOUNT_DIR)
            return
        
        microUpdate = False
        if isfile(f'{laserDir}/{MICRO_SOURCE}'):
            microUpdate = True
        
        if not microUpdate:
            os.system(f'cp -r {laserDir}/* {CURRENT_FILE_DIR}')
            os.system(f'umount {MOUNT_DIR}/sda*')
            shutil.rmtree(MOUNT_DIR)
            self.result.emit("Done GUI")

        else:
            file = open(f'{laserDir}/{MICRO_SOURCE}', 'rb')
            data = file.read()
            file.close()
            MICRO_DATA[250] = buildPacket(
                int_to_bytes(len(data)), 
                UPDATE_PAGE, 250, REPORT
            )
            MICRO_DATA[251] = buildPacket(
                int_to_bytes(PACKET_NOB), 
                UPDATE_PAGE, 251, REPORT
            )
            packet = bytearray()
            for field, i in enumerate(range(0, len(data), PACKET_NOB)):
                segment = data[i : i + PACKET_NOB]
                packet.append(0xAA)
                packet.append(0xBB)
                packet.append(5 + len(segment))
                packet.append(UPDATE_PAGE)
                packet.append(field)
                packet.append(REPORT)
                packet += segment
                crc = Crc16Xmodem.calc(packet[2:])
                crc_bytes = crc.to_bytes(2, byteorder='big')
                packet += crc_bytes
                packet.append(0xCC)
                MICRO_DATA[field] = packet
                packet[:] = []

            chan_list = [12,16]
            GPIO.output(chan_list, GPIO.LOW)
            self.sleep(1)
            GPIO.output(12, GPIO.HIGH)
            self.sleep(1)
            GPIO.output(16, GPIO.HIGH)
