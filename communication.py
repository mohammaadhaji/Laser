from PyQt5.QtCore import QThread, pyqtSignal
from crccheck.crc import Crc16Xmodem
from serial import Serial
import jdatetime

serial = Serial('COM2', 1152000)

HEADER_1   = 1
HEADER_2   = 2
CHECK_NOB  = 3
IN_MESSAGE = 4
STATE = HEADER_1

PAGE_INDEX     = 1
FIELD_INDEX    = 2
CMD_TYPE = 3

LASER_PAGE     = 0
SETTING_PAGE   = 1
LOCK_TIME_PAGE = 2
BODY_PART_PAGE = 3

REPORT = 0x0A
WRITE  = 0x0B 
READ   = 0x0C


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

    def selectionPage(self):
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

    def mainPage(self):
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
    
    def readTime(self):
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


    def laserPage(self, fieldValues):
        fieldsIndex = {
            'cooling': 3 , 'energy': 4, 'pulseWidth': 5,
            'frequency':6, 'couter': 7, 'ready-standby': 8
        }
        sendPacket(fieldsIndex, fieldValues, LASER_PAGE)

    def settingsPage(self, fieldValues, cmdType):
        fieldsIndex = {
           'serial': 0, 'totalCounter': 1, 'pDate': 2,
            'LaserEnergy': 3, 'waveLength': 4, 'LaserBarType': 5,
            'DriverVersion': 6, 'controlVersion': 7, 'firmware': 8,
            'monitor': 9, 'os': 10, 'gui': 11, 'rpi': 12
        }
        sendPacket(fieldsIndex, fieldValues, SETTING_PAGE, cmdType)

    def lockPage(self, cmdType):
        fieldsIndex = { 'clock': 0, 'date': 1}
        clock = jdatetime.datetime.now().strftime('%H : %M : %S')
        date  = jdatetime.datetime.now().togregorian().strftime('%Y-%m-%d')
        fieldValues = {'clock': clock, 'date': date}
        sendPacket(fieldsIndex, fieldValues, LOCK_TIME_PAGE, cmdType)
        

    def run(self):
        global STATE 
        packet = bytearray()
        serial.reset_input_buffer()

        while True:
            temp = serial.read_all()
            counter = 0

            try:
                if temp:
                    len_temp = len(temp)
                    while counter < len_temp:
                        if STATE == HEADER_1:

                            if temp[counter] == 0xAA:
                                STATE = HEADER_2

                        elif STATE == HEADER_2:

                            if temp[counter] == 0xBB:
                                STATE = CHECK_NOB
                                packet[:] = []

                        elif STATE == CHECK_NOB:
                            nob = temp[counter]
                            STATE = IN_MESSAGE

                        elif STATE == IN_MESSAGE:
                        
                            if len(packet) == nob:
                                STATE = HEADER_1
                                packet[0:0] = nob.to_bytes(
                                    length=1, 
                                    byteorder='big'
                                )

                                crc_s = int.from_bytes(
                                    packet[-2:], 
                                    byteorder='big', 
                                    signed=False
                                )

                                crc_r = Crc16Xmodem.calc(
                                    packet[:-2]
                                )
                                
                                if crc_r == crc_s:
                                    if packet[CMD_TYPE] == REPORT:
                                        
                                        if packet[PAGE_INDEX] == SETTING_PAGE:
                                            if packet[FIELD_INDEX] == 0:
                                                data = packet[4:-2].decode()
                                                d = data[-2:]
                                                m = data[-4:-2]
                                                y = data[-8:-4]
                                                serNum = data[:-8]
                                                pdate = y + ' / ' + m + ' / ' + d
                                                self.productionDate.emit(pdate)
                                                self.serialNumber.emit(serNum)

                                            elif packet[FIELD_INDEX] == 3:
                                                lEnergy = packet[4:-2].decode()
                                                self.laserEnergy.emit(lEnergy)

                                            elif packet[FIELD_INDEX] == 8:
                                                firmware = packet[4:-2].decode()
                                                self.firmwareVesion.emit(firmware)

                                        elif packet[PAGE_INDEX] == LOCK_TIME_PAGE:
                                            if packet[FIELD_INDEX] == 0:
                                                clock = packet[4:-2].decode()
                                                clock = clock.split(':')
                                                clock = tuple( int(x) for x in clock )
                                                self.sysClock.emit(clock)
                                            elif packet[FIELD_INDEX] == 1:
                                                date = packet[4:-2].decode()
                                                date = date.split('-')
                                                date = tuple( int(x) for x in date )
                                                self.sysDate.emit(date)

                                    elif packet[CMD_TYPE] == WRITE:

                                        if packet[PAGE_INDEX] in (LASER_PAGE, BODY_PART_PAGE):
                                            if packet[FIELD_INDEX] == 0:     
                                                flags = sensors(packet)
                                                self.sensorFlags.emit(flags)

                                            if packet[FIELD_INDEX] == 1:
                                                temp = packet[4:-2].decode()
                                                self.tempValue.emit(int(temp))

                                            if packet[FIELD_INDEX] == 7:
                                                shot = packet[4:-2].hex()
                                                if int(shot, 16) == 1:
                                                    self.shot.emit()

                                        elif packet[PAGE_INDEX] == SETTING_PAGE:
                                            if packet[FIELD_INDEX] == 0:
                                                data = packet[4:-2].decode()
                                                d = data[-2:]
                                                m = data[-4:-2]
                                                y = data[-8:-4]
                                                serNum = data[:-8]
                                                pdate = y + ' / ' + m + ' / ' + d
                                                self.productionDate.emit(pdate)
                                                self.serialNumber.emit(serNum)

                                            elif packet[FIELD_INDEX] == 3:
                                                lEnergy = packet[4:-2].decode()
                                                self.laserEnergy.emit(lEnergy)

                                            elif packet[FIELD_INDEX] == 8:
                                                firmware = packet[4:-2].decode()
                                                self.firmwareVesion.emit(firmware)
                                    
                                    elif packet[CMD_TYPE] == READ:
                                        if packet[PAGE_INDEX] == LASER_PAGE:

                                            if packet[FIELD_INDEX] == 3:
                                                self.readCooling.emit()
                                            elif packet[FIELD_INDEX] == 4:
                                                self.readEnergy.emit()
                                            elif packet[FIELD_INDEX] == 5:
                                                self.readPulseWidht.emit()
                                            elif packet[FIELD_INDEX] == 6:
                                                self.readFrequency.emit()

                                
                            else:
                                packet.append(temp[counter])

                        counter = counter + 1
            except Exception:
                pass
