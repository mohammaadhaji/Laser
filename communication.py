from PyQt5.QtCore import QObject, QThread, pyqtSignal
from crccheck.crc import Crc16Xmodem
from serial import Serial
import jdatetime, platform 

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

REPORT = 0x0A
WRITE  = 0x0B 
READ   = 0x0C

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

def sendPacket(fieldsIndex, fieldValues, page, cmdType=REPORT):
    packet = bytearray()
    for field, value in fieldValues.items():
        packet.append(0xAA)
        packet.append(0xBB)
        fieldValue = str(value).encode()
        packet.append(5 + len(fieldValue))
        packet.append(page)
        packet.append(fieldsIndex[field])
        packet.append(cmdType)
        packet += fieldValue
        crc = Crc16Xmodem.calc(packet[2:])
        crc_bytes = crc.to_bytes(2, byteorder='big')
        packet += crc_bytes
        packet.append(0xCC)
        serial.write(packet)
        packet[:] = []

def selectionPage():
    packet = bytearray(9)
    packet[0] = 0xAA
    packet[1] = 0xBB
    packet[2] = 0x05 # NoB
    packet[3] = 0x03 # Page Number
    packet[4] = 0xAA # Field
    packet[5] = 0x0A # Cmd type 
    crc = Crc16Xmodem.calc(packet[2:6])
    crc_bytes = crc.to_bytes(2, byteorder='big')
    packet[6] = crc_bytes[0]
    packet[7] = crc_bytes[1]
    packet[8] = 0xCC
    serial.write(packet)

def mainPage():
    packet = bytearray(9)
    packet[0] = 0xAA
    packet[1] = 0xBB
    packet[2] = 0x05 
    packet[3] = 0x04 
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

                            else:
                                RECEIVED_DATA.append(temp[counter])

                        counter = counter + 1
            except Exception as e:
                print(e)
