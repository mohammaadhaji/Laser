from PyQt5.QtCore import QObject, QThread, pyqtSignal
from crccheck.crc import Crc16Xmodem
from serial import Serial
from paths import CURRENT_FILE_DIR
from pathlib import Path
from utility import (
    log, calcMD5, int_to_bytes
)
import jdatetime, platform
import os, subprocess
import shutil, json
try:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    GPIO.output(12, GPIO.HIGH)
except Exception as e:
    pass
    log('GPIO', str(e) + '\n')
    

def gpioCleanup():
    try:
        GPIO.cleanup()
    except Exception as e:
        log('GPIO', str(e) + '\n')
        pass

if platform.system() == 'Windows':
    serial = Serial('COM2', 115200)
else:
    serial = Serial('/dev/ttyS0', 460800)

HEADER_1       = 1
HEADER_2       = 2
CHECK_NOB_1    = 3
CHECK_NOB_2    = 4
IN_MESSAGE     = 5
STATE          = HEADER_1

PAGE_INDEX     = 2
FIELD_INDEX    = 3
CMD_TYPE_INDEX = 4
DATA_INDEX     = 5

LASER_PAGE         = 0
SETTING_PAGE       = 1
LOCK_TIME_PAGE     = 2
BODY_PART_PAGE     = 3
MAIN_PAGE          = 4
SHUTDONW_PAGE      = 5
UPDATE_PAGE        = 6
HARDWARE_TEST_PAGE = 7
LASER_CALIB_PAGE   = 8
OTHER_PAGE         = 9


REPORT         = 0x0A
WRITE          = 0x0B 
READ           = 0x0C

MOUNT_DIR      = '/media/updateFirmware'
SOURCE_ZIP     = 'Laser.zip'
VERIFY         = 'verify'
MICRO_SOURCE   = 'Laser_Application.bin'
MICRO_DATA     = {}
PACKET_NOB     = 1000

RECEIVED_DATA  = bytearray()
NOB_BYTES      = bytearray(2)


def printPacket(packet):
    print( " ".join(packet.hex()[i:i+2].upper() for i in range(0, len(packet.hex()), 2)))

def sensors(packet):
    flags = [False] * 6
    for i in range(6):
        if packet[5 + i]:
            flags[i] = False
        else:
            flags[i] = True

    return flags


def buildPacket(data, page, field, cmdType):
    packet = bytearray()
    packet.append(0xAA)
    packet.append(0xBB)
    packet += (5 + len(data)).to_bytes(2, byteorder='big')
    packet.append(page)
    packet.append(field)
    packet.append(cmdType)
    packet += data
    crc = Crc16Xmodem.calc(packet[2:])
    crc_bytes = crc.to_bytes(2, byteorder='big')
    packet += crc_bytes
    packet.append(0xCC)
    # print('SENT: ', end='')
    # printPacket(packet)
    return packet


def sendPacket(fieldsIndex, fieldValues, page, cmdType=REPORT):
    
    for field, value in fieldValues.items():
        packet = buildPacket(str(value).encode(), page, fieldsIndex[field], cmdType)
        serial.write(packet)


def enterPage(page):
    packet = buildPacket(b'', page, 0xAA, REPORT)
    serial.write(packet)


def readTime():
    packet1 = buildPacket(b'', LOCK_TIME_PAGE, 0x01, READ)
    packet2 = buildPacket(b'', LOCK_TIME_PAGE, 0x00, READ)
    serial.write(packet1)
    serial.write(packet2)
    

def laserPage(fieldValues):
    fieldsIndex = {
        'cooling': 3 , 'energy': 4, 'pulseWidth': 5,
        'frequency':6, 'couter': 7, 'ready-standby': 8
    }
    sendPacket(fieldsIndex, fieldValues, LASER_PAGE)


def laserCalibPage(fieldValues):
    fieldsIndex = {
        'energy': 2, 'pulseWidth': 3,
        'frequency': 3, 'ready-standby': 5
    }
    sendPacket(fieldsIndex, fieldValues, LASER_CALIB_PAGE)


def settingsPage(fieldValues, cmdType):
    fieldsIndex = {
        'serial': 0, 'totalCounter': 1, 'pDate': 2,
        'LaserEnergy': 3, 'waveLength': 4, 'LaserBarType': 5,
        'DriverVersion': 6, 'controlVersion': 7, 'firmware': 8,
        'monitor': 9, 'os': 10, 'gui': 11, 'rpi': 12, 'SpotSize': 13
    }
    sendPacket(fieldsIndex, fieldValues, SETTING_PAGE, cmdType)


def lockPage(cmdType):
    fieldsIndex = { 'clock': 0, 'date': 1}
    clock = jdatetime.datetime.now().strftime('%H : %M : %S')
    date  = jdatetime.datetime.now().togregorian().strftime('%Y-%m-%d')
    fieldValues = {'clock': clock, 'date': date}
    sendPacket(fieldsIndex, fieldValues, LOCK_TIME_PAGE, cmdType)

def decodePacket(RECEIVED_DATA):
    key = ''
    value = 0
    if RECEIVED_DATA[CMD_TYPE_INDEX] == REPORT:

        if RECEIVED_DATA[PAGE_INDEX] == SETTING_PAGE:
            if RECEIVED_DATA[FIELD_INDEX] == 0:
                serNum = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'serialNumber', serNum

            elif RECEIVED_DATA[FIELD_INDEX] == 2:
                pDate = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'productionDate', pDate

            elif RECEIVED_DATA[FIELD_INDEX] == 3:
                lEnergy = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'laserEnergy', lEnergy

            elif RECEIVED_DATA[FIELD_INDEX] == 4:
                lEnergy = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'laserWavelenght', lEnergy

            elif RECEIVED_DATA[FIELD_INDEX] == 5:
                lEnergy = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'laserBarType', lEnergy

            elif RECEIVED_DATA[FIELD_INDEX] == 6:
                lEnergy = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'driverVersion', lEnergy

            elif RECEIVED_DATA[FIELD_INDEX] == 7:
                lEnergy = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'mainControl', lEnergy 

            elif RECEIVED_DATA[FIELD_INDEX] == 8:
                firmware = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'firmwareVesion', firmware

            elif RECEIVED_DATA[FIELD_INDEX] == 13:
                spotSize = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'spotSize', spotSize

        elif RECEIVED_DATA[PAGE_INDEX] == HARDWARE_TEST_PAGE:
            if RECEIVED_DATA[FIELD_INDEX] in [0, 1, 2, 3, 4]:
                date = RECEIVED_DATA[DATA_INDEX:-2].decode()
                step, status = date[0], date[1]
                relays = ['handPiece', 'radiator', 'laserPower', 'airCooling', 'reservedRelay']
                key, value = relays[RECEIVED_DATA[FIELD_INDEX]], [int(step), int(status)]

            elif RECEIVED_DATA[FIELD_INDEX] == 6:
                driverCurrent = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'driverCurrent', float(driverCurrent)

            elif RECEIVED_DATA[FIELD_INDEX] == 7:
                dacVoltage = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'dacVoltage', float(dacVoltage)

            elif RECEIVED_DATA[FIELD_INDEX] == 8:
                flowMeter = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'flowMeter', flowMeter

            elif RECEIVED_DATA[FIELD_INDEX] == 9:
                waterTempSensor = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'waterTempSensor', waterTempSensor

            elif RECEIVED_DATA[FIELD_INDEX] == 10:
                handpieceTemp = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'handpieceTemp', handpieceTemp

            elif RECEIVED_DATA[FIELD_INDEX] == 11:
                airTempSensor = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'airTempSensor', airTempSensor

            elif RECEIVED_DATA[FIELD_INDEX] == 12:
                flags = sensors(RECEIVED_DATA)
                key, value = 'sensorFlagsTest', flags[:2]

        elif RECEIVED_DATA[PAGE_INDEX] == LOCK_TIME_PAGE:
            if RECEIVED_DATA[FIELD_INDEX] == 0:
                clock = RECEIVED_DATA[DATA_INDEX:-2].decode()
                clock = clock.split(':')
                clock = tuple( int(x) for x in clock )
                key, value = 'sysClock', clock

            elif RECEIVED_DATA[FIELD_INDEX] == 1:
                date = RECEIVED_DATA[DATA_INDEX:-2].decode()
                date = date.split('-')
                date = tuple( int(x) for x in date )
                key, value = 'sysDate', date
        
        elif RECEIVED_DATA[PAGE_INDEX] == UPDATE_PAGE:
            if RECEIVED_DATA[FIELD_INDEX] == 252:
                status = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'updateProgress', status

    elif RECEIVED_DATA[CMD_TYPE_INDEX] == WRITE:

        if RECEIVED_DATA[PAGE_INDEX] in (LASER_PAGE, LASER_CALIB_PAGE, BODY_PART_PAGE):
            if RECEIVED_DATA[FIELD_INDEX] == 0:     
                flags = sensors(RECEIVED_DATA)
                key, value = 'sensorFlags', flags
                
            if RECEIVED_DATA[FIELD_INDEX] == 1:
                t = RECEIVED_DATA[DATA_INDEX:-2].decode()
                key, value = 'tempValue', int(t)

            if RECEIVED_DATA[FIELD_INDEX] == 7:
                shot = RECEIVED_DATA[DATA_INDEX:-2].hex()
                if int(shot, 16) == 1:
                    key = 'shot'

    elif RECEIVED_DATA[CMD_TYPE_INDEX] == READ:

        if RECEIVED_DATA[PAGE_INDEX] == LASER_PAGE:

            if RECEIVED_DATA[FIELD_INDEX] == 3:
                key = 'readCooling'
            elif RECEIVED_DATA[FIELD_INDEX] == 4:
                key = 'readEnergy'
            elif RECEIVED_DATA[FIELD_INDEX] == 5:
                key = 'readPulseWidht'
            elif RECEIVED_DATA[FIELD_INDEX] == 6:
                key = 'readFrequency'

        elif RECEIVED_DATA[PAGE_INDEX] == UPDATE_PAGE:
            segmentIndex = RECEIVED_DATA[FIELD_INDEX]
            if segmentIndex in MICRO_DATA.keys():
                serial.write(MICRO_DATA[segmentIndex])
            elif RECEIVED_DATA[FIELD_INDEX] == 250:
                serial.write(MICRO_DATA[250])
            elif RECEIVED_DATA[FIELD_INDEX] == 251:
                serial.write(MICRO_DATA[251])

    return key, value

class SerialTimer(QObject):
    sysClock         = pyqtSignal(tuple)
    sysDate          = pyqtSignal(tuple)
    driverCurrent    = pyqtSignal(float)
    dacVoltage       = pyqtSignal(float)
    sensorFlags      = pyqtSignal(list)
    handPiece        = pyqtSignal(list)
    radiator         = pyqtSignal(list)
    laserPower       = pyqtSignal(list)
    airCooling       = pyqtSignal(list)
    reservedRelay    = pyqtSignal(list)
    interLockTest    = pyqtSignal(bool)
    waterLevelTest   = pyqtSignal(bool)
    airTempSensor    = pyqtSignal(int)
    tempValue        = pyqtSignal(int)
    flowMeter        = pyqtSignal(str)
    waterTempSensor  = pyqtSignal(str)
    handpieceTemp    = pyqtSignal(str)
    airTempSensor    = pyqtSignal(str)
    serialNumber     = pyqtSignal(str)
    productionDate   = pyqtSignal(str)
    laserEnergy      = pyqtSignal(str)
    laserWavelenght  = pyqtSignal(str)
    laserBarType     = pyqtSignal(str)
    driverVersion    = pyqtSignal(str)
    mainControl      = pyqtSignal(str)
    firmwareVesion   = pyqtSignal(str)
    updateProgress   = pyqtSignal(str)
    spotSize         = pyqtSignal(str)
    readCooling      = pyqtSignal()
    readEnergy       = pyqtSignal()
    readPulseWidht   = pyqtSignal()
    readFrequency    = pyqtSignal()
    shot             = pyqtSignal()
    receivingSensors = pyqtSignal()

    def __init__(self):
        super(QObject, self).__init__()


    def closePort(self):
        serial.close()

    def checkBuffer(self):
        if serial.is_open and serial.in_waiting > 1:
            self.readDate()

    def readDate(self):
        global STATE, RECEIVED_DATA, NOB_BYTES
        nob  = 0
        nob1 = 0 
        nob2 = 0

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
                            STATE = CHECK_NOB_1
                            RECEIVED_DATA[:] = []

                    elif STATE == CHECK_NOB_1:
                        nob1 = temp[counter]
                        STATE = CHECK_NOB_2
                    
                    elif STATE == CHECK_NOB_2:
                        nob2 = temp[counter]
                        NOB_BYTES[0] = nob1
                        NOB_BYTES[1] = nob2
                        nob = int.from_bytes(NOB_BYTES, "big")  
                        STATE = IN_MESSAGE

                    elif STATE == IN_MESSAGE:
                    
                        if len(RECEIVED_DATA) == nob:
                            STATE = HEADER_1
                            RECEIVED_DATA[0:0] = nob.to_bytes(2, 'big')

                            crc_s = int.from_bytes(
                                RECEIVED_DATA[-2:], 
                                byteorder='big', 
                                signed=False
                            )

                            crc_r = Crc16Xmodem.calc(
                                RECEIVED_DATA[:-2]
                            )
                            
                            if crc_r == crc_s:
                                # print('RECE: ', end='')
                                # printPacket(RECEIVED_DATA)
                                key, value = decodePacket(RECEIVED_DATA)
                                if key == 'sensorFlags':
                                    self.sensorFlags.emit(value)
                                    self.receivingSensors.emit()
                                elif key == 'sysDate':
                                    self.sysDate.emit(value)
                                elif key == 'sysClock':
                                    self.sysClock.emit(value)
                                elif key == 'tempValue':
                                    self.tempValue.emit(value)
                                elif key == 'serialNumber':
                                    self.serialNumber.emit(value)
                                elif key == 'productionDate':
                                    self.productionDate.emit(value)
                                elif key == 'laserEnergy':
                                    self.laserEnergy.emit(value)
                                elif key == 'laserWavelenght':
                                    self.laserWavelenght.emit(value)
                                elif key == 'laserBarType':
                                    self.laserBarType.emit(value)
                                elif key == 'spotSize':
                                    self.spotSize.emit(value)
                                elif key == 'driverVersion':
                                    self.driverVersion.emit(value)
                                elif key == 'mainControl':
                                    self.mainControl.emit(value)
                                elif key == 'firmwareVesion':
                                    self.firmwareVesion.emit(value)
                                elif key == 'updateProgress':
                                    self.updateProgress.emit(value)
                                elif key == 'readCooling':
                                    self.readCooling.emit()
                                elif key == 'readEnergy':
                                    self.readEnergy.emit()
                                elif key == 'readPulseWidht':
                                    self.readPulseWidht.emit()
                                elif key == 'readFrequency':
                                    self.readFrequency.emit()
                                elif key == 'shot':
                                    self.shot.emit()
                                elif key == 'handPiece':
                                    self.handPiece.emit(value)
                                elif key == 'radiator':
                                    self.radiator.emit(value)
                                elif key == 'laserPower':
                                    self.laserPower.emit(value)
                                elif key == 'airCooling':
                                    self.airCooling.emit(value)
                                elif key == 'reservedRelay':
                                    self.reservedRelay.emit(value)
                                elif key == 'driverCurrent':
                                    self.driverCurrent.emit(value)
                                elif key == 'dacVoltage':
                                    self.dacVoltage.emit(value)
                                elif key == 'flowMeter':
                                    self.flowMeter.emit(value)
                                elif key == 'waterTempSensor':
                                    self.waterTempSensor.emit(value)
                                elif key == 'handpieceTemp':
                                    self.handpieceTemp.emit(value)
                                elif key == 'airTempSensor':
                                    self.airTempSensor.emit(value)
                                elif key == 'sensorFlagsTest':
                                    self.interLockTest.emit(value[0])
                                    self.waterLevelTest.emit(value[1])
                        else:
                            RECEIVED_DATA.append(temp[counter])

                    counter = counter + 1
        except Exception as e:
            print(e)
            log('Serial Unhandled Exception', str(e) + '\n')


class SerialThread(QThread):
    sysClock         = pyqtSignal(tuple)
    sysDate          = pyqtSignal(tuple)
    driverCurrent    = pyqtSignal(float)
    dacVoltage       = pyqtSignal(float)
    sensorFlags      = pyqtSignal(list)
    handPiece        = pyqtSignal(list)
    radiator         = pyqtSignal(list)
    laserPower       = pyqtSignal(list)
    airCooling       = pyqtSignal(list)
    reservedRelay    = pyqtSignal(list)
    interLockTest    = pyqtSignal(bool)
    waterLevelTest   = pyqtSignal(bool)
    airTempSensor    = pyqtSignal(int)
    tempValue        = pyqtSignal(int)
    flowMeter        = pyqtSignal(str)
    waterTempSensor  = pyqtSignal(str)
    handpieceTemp    = pyqtSignal(str)
    airTempSensor    = pyqtSignal(str)
    serialNumber     = pyqtSignal(str)
    productionDate   = pyqtSignal(str)
    laserEnergy      = pyqtSignal(str)
    laserWavelenght  = pyqtSignal(str)
    laserBarType     = pyqtSignal(str)
    driverVersion    = pyqtSignal(str)
    mainControl      = pyqtSignal(str)
    firmwareVesion   = pyqtSignal(str)
    updateProgress   = pyqtSignal(str)
    spotSize         = pyqtSignal(str)
    readCooling      = pyqtSignal()
    readEnergy       = pyqtSignal()
    readPulseWidht   = pyqtSignal()
    readFrequency    = pyqtSignal()
    shot             = pyqtSignal()
    receivingSensors = pyqtSignal()

    def __init__(self, parent = None):
        super(SerialThread, self).__init__(parent)
        self.loop = True


    def closePort(self):
        self.loop = False
        serial.close()


    def run(self):
        global STATE, RECEIVED_DATA, NOB_BYTES
        nob  = 0
        nob1 = 0 
        nob2 = 0
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
                                STATE = CHECK_NOB_1
                                RECEIVED_DATA[:] = []

                        elif STATE == CHECK_NOB_1:
                            nob1 = temp[counter]
                            STATE = CHECK_NOB_2
                        
                        elif STATE == CHECK_NOB_2:
                            nob2 = temp[counter]
                            NOB_BYTES[0] = nob1
                            NOB_BYTES[1] = nob2
                            nob = int.from_bytes(NOB_BYTES, "big")
                            STATE = IN_MESSAGE

                        elif STATE == IN_MESSAGE:
                        
                            if len(RECEIVED_DATA) == nob:
                                STATE = HEADER_1
                                RECEIVED_DATA[0:0] = nob.to_bytes(2, 'big')

                                crc_s = int.from_bytes(
                                    RECEIVED_DATA[-2:], 
                                    byteorder='big', 
                                    signed=False
                                )

                                crc_r = Crc16Xmodem.calc(
                                    RECEIVED_DATA[:-2]
                                )

                                if crc_r == crc_s:
                                    # print('RECE: ', end='')
                                    # printPacket(RECEIVED_DATA)
                                    key, value = decodePacket(RECEIVED_DATA)
                                    if key == 'sensorFlags':
                                        self.sensorFlags.emit(value)
                                        self.receivingSensors.emit()
                                    elif key == 'sysDate':
                                        self.sysDate.emit(value)
                                    elif key == 'sysClock':
                                        self.sysClock.emit(value)
                                    elif key == 'tempValue':
                                        self.tempValue.emit(value)
                                    elif key == 'serialNumber':
                                        self.serialNumber.emit(value)
                                    elif key == 'productionDate':
                                        self.productionDate.emit(value)
                                    elif key == 'laserEnergy':
                                        self.laserEnergy.emit(value)
                                    elif key == 'laserWavelenght':
                                        self.laserWavelenght.emit(value)
                                    elif key == 'laserBarType':
                                        self.laserBarType.emit(value)
                                    elif key == 'spotSize':
                                        self.spotSize.emit(value)
                                    elif key == 'driverVersion':
                                        self.driverVersion.emit(value)
                                    elif key == 'mainControl':
                                        self.mainControl.emit(value)
                                    elif key == 'firmwareVesion':
                                        self.firmwareVesion.emit(value)
                                    elif key == 'updateProgress':
                                        self.updateProgress.emit(value)
                                    elif key == 'readCooling':
                                        self.readCooling.emit()
                                    elif key == 'readEnergy':
                                        self.readEnergy.emit()
                                    elif key == 'readPulseWidht':
                                        self.readPulseWidht.emit()
                                    elif key == 'readFrequency':
                                        self.readFrequency.emit()
                                    elif key == 'shot':
                                        self.shot.emit()
                                    elif key == 'handPiece':
                                        self.handPiece.emit(value)
                                    elif key == 'radiator':
                                        self.radiator.emit(value)
                                    elif key == 'laserPower':
                                        self.laserPower.emit(value)
                                    elif key == 'airCooling':
                                        self.airCooling.emit(value)
                                    elif key == 'reservedRelay':
                                        self.reservedRelay.emit(value)
                                    elif key == 'driverCurrent':
                                        self.driverCurrent.emit(value)
                                    elif key == 'dacVoltage':
                                        self.dacVoltage.emit(value)
                                    elif key == 'flowMeter':
                                        self.flowMeter.emit(value)
                                    elif key == 'waterTempSensor':
                                        self.waterTempSensor.emit(value)
                                    elif key == 'handpieceTemp':
                                        self.handpieceTemp.emit(value)
                                    elif key == 'airTempSensor':
                                        self.handpieceTemp.emit(value)
                                    elif key == 'sensorFlagsTest':
                                        self.interLockTest.emit(value[0])
                                        self.waterLevelTest.emit(value[1])
                            else:
                                RECEIVED_DATA.append(temp[counter])

                        counter = counter + 1
            except Exception as e:
                print(e)
                log('Serial Unhandled Exception', str(e) + '\n')


def updateCleanup(mountPoint, laserD=''):
    try:
        if os.path.isdir(laserD):
            shutil.rmtree(laserD)

        for mp in mountPoint.values():
            os.system(f'umount {mp}')

        if os.path.isdir(MOUNT_DIR):
            shutil.rmtree(MOUNT_DIR)
        
    except Exception as e:
        log('Update Firmware', str(e) + '\n')


class UpdateFirmware(QThread):
    result = pyqtSignal(str)

    def run(self):
        global MICRO_DATA
        MICRO_DATA.clear()
        try:
            if platform.system() == 'Windows':
                self.result.emit("We don't do that here.")
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
                log('Update Firmware', err + '\n')
                return
                    
            if not 'children' in sdaBlock:
                err = "Flash drive doesn't have any partitions."
                self.result.emit(err)
                log('Update Firmware', err + '\n')
                return

            if not os.path.isdir(MOUNT_DIR):    
                os.mkdir(MOUNT_DIR)

            partitionsDir = {}
            for part in sdaBlock['children']:
                partitionsDir[part['name']] = part['mountpoint']

            for part in partitionsDir:
                if partitionsDir[part] == None:
                    if not os.path.isdir(f'{MOUNT_DIR}/{part}'):
                        os.mkdir(f'{MOUNT_DIR}/{part}')
                    r = subprocess.call(
                        f'mount /dev/{part} {MOUNT_DIR}/{part}',
                        shell=True
                    )
                    partitionsDir[part] = f'{MOUNT_DIR}/{part}'

            laserFound = False
            laserTarDir = ''
            laserDir = ''
            laserUnpackDir = ''
            for dir in partitionsDir.values():
                if os.path.isfile(f'{dir}/{SOURCE_ZIP}'):
                    laserFound = True
                    laserTarDir = f'{dir}/{SOURCE_ZIP}'
                    laserDir = str(Path(laserTarDir).with_suffix(''))
                    laserUnpackDir = Path(laserTarDir).parent.absolute()

            if not laserFound:
                err = "Source files not found."
                self.result.emit(err)
                log('Update Firmware', err + '\n')
                updateCleanup(partitionsDir)
                return

            
            if os.path.isdir(laserDir):
                shutil.rmtree(laserDir)

            shutil.unpack_archive(laserTarDir, laserUnpackDir)

            microUpdate = False
            if os.path.isfile(f'{laserDir}/{MICRO_SOURCE}'):
                microUpdate = True

            if not microUpdate:
                try:
                    verifyError = 'The source files are corrupted and can not be replaced.'
                    with open(f'{laserDir}/{VERIFY}', 'r') as f:
                        md5 = int(f.read())

                    if not md5 == calcMD5(laserDir, f'{VERIFY}'):
                        self.result.emit(verifyError)
                        log('Update Firmware', verifyError + '\n')
                        updateCleanup(partitionsDir, laserD=laserDir)
                        return

                except Exception as e:
                    self.result.emit(verifyError)
                    log('Update Firmware', str(e) + '\n')
                    updateCleanup(partitionsDir)
                    return

                os.system(f'cp -r {laserDir}/* {CURRENT_FILE_DIR}')
                updateCleanup(partitionsDir, laserD=laserDir)
                self.result.emit("Done GUI")

            else:
                file = open(f'{laserDir}/{MICRO_SOURCE}', 'rb')
                data = file.read()
                file.close()

                for field, i in enumerate(range(0, len(data), PACKET_NOB)):
                    segment = data[i : i + PACKET_NOB]                
                    MICRO_DATA[field] = buildPacket(
                        segment, UPDATE_PAGE, field, REPORT
                    )
                
                MICRO_DATA[250] = buildPacket(
                    int_to_bytes(len(data)), 
                    UPDATE_PAGE, 250, REPORT
                )
                MICRO_DATA[251] = buildPacket(
                    int_to_bytes(PACKET_NOB), 
                    UPDATE_PAGE, 251, REPORT
                )
                enterPage(UPDATE_PAGE)
                GPIO.output(12, GPIO.LOW)
                self.msleep(50)
                GPIO.output(12, GPIO.HIGH)
                updateCleanup(partitionsDir, laserD=laserDir)

        except Exception as e:
            self.result.emit('Operation failed. Please restart and try again.')
            updateCleanup(partitionsDir, laserD=laserDir)
            log('Update Firmware, Unhandled Exception', str(e) + '\n')
