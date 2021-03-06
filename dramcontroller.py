import serial
import numpy as np
from serial.tools.list_ports import comports


class DramController:
    port = ""
    ser = None
    buttonRed = 0
    buttonBlue = 0
    buttonGreen = 0
    buttonOrange = 0

    vibrator = 0
    vibratorCounter = 0
    buzzer = 0

    buttonRedLed = 0
    buttonBlueLed = 0
    buttonGreenLed = 0
    buttonOrangeLed = 0

    IMU = np.zeros((3, 3), float)
    MIC = 0
    NunChuk = None
    oldString = ""

    def __init__(self):
        self.port = self.getPort("Arduino Zero")
        self.NunChuk = NunChuk()
        if (self.port != ''):
            self.ser = serial.Serial(self.port, 115200, timeout=0)
            if (self.ser.is_open):
                self.ser.close()
                self.ser.open()

    def setvalues(self, bo, bb, br, bg):
        self.buttonOrange = bo
        self.buttonBlue = bb
        self.buttonRed = br
        self.buttonGreen = bg

    def getPort(self, name):
        portName = ''
        portList = list(comports())
        for port in portList:
            if port[1].startswith(name):
                portName = port[0]
        return (portName)

    def mapStamina(self, stamina):
        if (stamina > 80):
            self.leds = [1, 1, 1, 1, 1]
        elif (stamina > 60):
            self.leds = [1, 1, 1, 1, 0]
        elif (stamina > 40):
            self.leds = [1, 1, 1, 0, 0]
        elif (stamina > 20):
            self.leds = [1, 1, 0, 0, 0]
        elif (stamina > 1):
            self.leds = [1, 0, 0, 0, 0]
        else:
            self.leds = [0, 0, 0, 0, 0]

    def mapHealth(self, hp):
        if (hp > 99):
            self.seg1 = 9
            self.seg2 = 9
        else:
            self.seg1 = int(hp / 10)
            self.seg2 = int(hp - int(hp / 10) * 10)

    def sendData(self):
        if (self.ser != None):
            if (self.vibrator == 1 and self.vibratorCounter > 0):
                self.vibratorCounter -= 1
            else:
                self.vibrator = 0
            text = "{LEDS:" + str(self.leds[0]) + str(self.leds[1]) + str(self.leds[2]) + str(self.leds[3]) + str(
                self.leds[4]) + ",BUTTONLEDS:" + str(self.buttonRedLed) + str(self.buttonGreenLed) + str(
                self.buttonOrangeLed) + str(self.buttonBlueLed) + ",SEG1:" + str(self.seg1) + ",SEG2:" + str(
                self.seg2) + ",VIBRATION:" + str(self.vibrator) + ",BUZZER:" + str(self.buzzer) + "};"
            if (text != self.oldString):
                self.oldString = text
                data = bytes(text, encoding='utf-8')
                self.ser.write(data)

    def updateIMU(self, x, y, z):
        for i in range(2):
            for j in range(3):
                self.IMU[i, j] = self.IMU[i + 1, j]
        self.IMU[2, 0] = x
        self.IMU[2, 1] = y
        self.IMU[2, 2] = z

    def detectMotion(self):
        vals = np.array(
            [self.IMU[2, 0] - self.IMU[1, 0], self.IMU[2, 1] - self.IMU[1, 1], self.IMU[2, 2] - self.IMU[1, 2]])
        # print(np.linalg.norm(vals))
        if (np.linalg.norm(vals) > 15):
            return True
        else:
            return False

    def readData(self):
        if (self.ser != None):
            while (self.ser.inWaiting()):
                line = self.ser.readline()
                if (len(line) >= 70):
                    string = str(line).split(",")
                    # print(string)
                    if (len(string) >= 8 and string[0].startswith("b'{BUTTONS:")):
                        try:
                            buttons = string[0]
                            joyx = string[1]
                            joyy = string[2]
                            pitch = string[3]
                            roll = string[4]
                            Z = string[5]
                            C = string[6]
                            if (len(string) >= 11):
                                self.MIC = int(string[7].replace("SOUND:", ''))
                                IMUX = float(string[8].replace("IMUX:", ''))
                                IMUY = float(string[9].replace("IMUY:", ''))
                                IMUZ = float(
                                    string[10].replace("IMUZ:", '').replace("};\\r\\n'", '').replace("'", '').replace(
                                        "};", ''))
                                self.updateIMU(IMUX, IMUY, IMUZ)

                            buttons = buttons.replace("b'{BUTTONS:", '')
                            joyx = joyx.replace('JOYX:', '')
                            joyy = joyy.replace('JOYY:', '')
                            pitch = pitch.replace('PITCH:', '')
                            roll = roll.replace('ROLL:', '')
                            Z = Z.replace('Z:', '')
                            C = C.replace('C:', '')
                            joyx = int(joyx)
                            joyy = int(joyy)
                            pitch = float(pitch)
                            roll = float(roll)
                            Z = int(Z)
                            C = int(C)
                            self.NunChuk.setvalues(joyx, joyy, Z, C, (0, 0, 0), pitch, roll)
                            if (len(str(buttons)) == 4):
                                self.setvalues(int(buttons[0]), int(buttons[1]), int(buttons[2]), int(buttons[3]))
                        except:
                            print("Invalid string from controller", string)


class NunChuk:
    joyX = 129
    joyY = 131
    buttonZ = 0
    buttonC = 0
    accel = (0, 0, 0)
    roll = 0
    pitch = 0

    def __init__(self):
        self.roll = 0

    def setvalues(self, X, Y, Z, C, acc, p, r):
        self.joyX = X
        self.joyY = Y
        self.buttonZ = Z
        self.buttonC = C
        self.accel = acc
        self.pitch = p
        self.roll = r
