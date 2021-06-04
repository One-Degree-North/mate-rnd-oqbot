import sys
sys.path.insert(0, './mcu-lib')
from mcu import MCUInterface
import random
# import threading
# import serial
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QTimer, QEvent
import PyQt5.QtMultimedia as QTM
import PyQt5.QtMultimediaWidgets as QTMW
import PyQt5.QtWidgets as QT
from PyQt5.QtGui import QKeyEvent


# ser = serial.Serial('/dev/ttyACM0')
# ser.flushInput()

app = QT.QApplication(sys.argv)


#    def run(self):
#        self.ser_bytes = ser.readline()
#        self.decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
#        MainWindow.sertext.appendPlainText(decoded_bytes)
#        print(self.decoded_bytes)


class MainWindow(QT.QWidget):
    def __init__(self, mcuobject, comms: Communications, exit_program: ExitProgram):
        super().__init__()
        self.mcu = mcuobject
        self.thruster1speed = 0
        self.thruster2speed = 0
        self.thruster3speed = 0
        self.thruster4speed = 0
        self.servospeed = 0
        
        self.comms = comms
        self.exit_program = exit_program
        
        # (key, message sent to comms)
        self.keys_pressed = [
            ("W", "lw"),
            ("w", "w"),
            ("A", "la"),
            ("a", "a"),
            ("S", "ls"),
            ("s", "s"),
            ("D", "ld"),
            ("d", "d"),
            ("E", "le"),
            ("e", "e"),
            ("Q", "lq"),
            ("q", "q"),
            (" ", "spacebar")
        ]
        
        self.keys_released = [
            ("w", "sw"),
            ("a", "sa"),
            ("s", "ss"),
            ("d", "sd"),
            ("e", "se"),
            ("q", "sq")
        ]
    
    def updatetext(self):
        self.voltage_info.setText(str(self.mcu.latest_voltage))
        self.x_gyro.setText(str(self.mcu.latest_gyro[0]))
        self.y_gyro.setText(str(self.mcu.latest_gyro[1]))
        self.z_gyro.setText(str(self.mcu.latest_gyro[2]))
        self.x_accel.setText(str(self.mcu.latest_accel[0]))
        self.y_accel.setText(str(self.mcu.latest_accel[1]))
        self.z_accel.setText(str(self.mcu.latest_accel[2]))
        self.temperature.setText(str(self.mcu.latest_temp))
        self.thruster1.setText(str(self.thruster1speed))
        self.thruster2.setText(str(self.thruster2speed))
        self.thruster3.setText(str(self.thruster3speed))
        self.thruster4.setText(str(self.thruster4speed))
        self.servo.setText(str(self.servospeed))
    
    def setupui(self):
        self.setWindowTitle('MATE')
        self.setGeometry(0, 0, 1600, 800)
        self.show()
        
        self.general_list = QT.QFormLayout()
        self.voltage_info = QT.QLabel()
        self.general_list.addRow(QT.QLabel("Voltage:"),self.voltage_info)
        self.general_box = QT.QGroupBox("General")
        self.general_box.setLayout(self.general_list)

        self.imu_list = QT.QFormLayout()
        self.x_gyro = QT.QLabel()
        self.y_gyro = QT.QLabel()
        self.z_gyro = QT.QLabel()
        self.x_accel = QT.QLabel()
        self.y_accel = QT.QLabel()
        self.z_accel = QT.QLabel()
        self.temperature = QT.QLabel()
        self.imu_list.addRow(QT.QLabel("X Rotation:"),self.x_gyro)
        self.imu_list.addRow(QT.QLabel("Y Rotation:"),self.y_gyro)
        self.imu_list.addRow(QT.QLabel("Z Rotation:"),self.z_gyro)
        self.imu_list.addRow(QT.QLabel("X Accerleration:"),self.x_accel)
        self.imu_list.addRow(QT.QLabel("Y Accerleration:"),self.y_accel)
        self.imu_list.addRow(QT.QLabel("Z Accerleration:"),self.z_accel)
        self.imu_list.addRow(QT.QLabel("Temperature:"),self.temperature)
        self.imu_box = QT.QGroupBox("IMU")
        self.imu_box.setLayout(self.imu_list)

        self.pwm_list = QT.QFormLayout()
        self.thruster1 = QT.QLabel()
        self.thruster2 = QT.QLabel()
        self.thruster3 = QT.QLabel()
        self.thruster4 = QT.QLabel()
        self.servo = QT.QLabel()
        self.pwm_list.addRow(QT.QLabel("Thruster 1:"),self.thruster1)
        self.pwm_list.addRow(QT.QLabel("Thruster 2:"),self.thruster2)
        self.pwm_list.addRow(QT.QLabel("Thruster 3:"),self.thruster3)
        self.pwm_list.addRow(QT.QLabel("Thruster 4:"),self.thruster4)
        self.pwm_list.addRow(QT.QLabel("Servo:"),self.servo)

        self.pwmbox = QT.QGroupBox("PWM")
        self.pwmbox.setLayout(self.pwm_list)


        self.camera = QTM.QCamera()
        self.camera_view = QTMW.QCameraViewfinder()
        self.camera.setViewfinder(self.camera_view)
        self.camera.setCaptureMode(QTM.QCamera.CaptureViewfinder)
        self.camera.start()


        self.sertext = QT.QPlainTextEdit("text")
        self.sertext.setReadOnly(True)
        
        self.layout = QT.QGridLayout()
        self.layout.addWidget(self.camera_view,1,1,4,2)
        self.layout.addWidget(self.general_box,1,4,1,1)
        self.layout.addWidget(self.imu_box,2,4,1,1)
        self.layout.addWidget(self.pwmbox,3,4,1,1)
        self.layout.addWidget(self.sertext,1,3,4,1)
        self.layout.setColumnMinimumWidth(3,400)
        self.layout.setColumnMinimumWidth(4,300)
        self.setLayout(self.layout)
        
        self.keyPressEvent
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.updatetext)
        self.timer.start(100)
    
    def on_trigger(self, trigger):
        self.comms.read_send(trigger)
    
    def keyPressEvent(self, keyevent):
        if keyevent.key() == Qt.Key_Escape:
            self.exit_program.Exit()
        
        if not keyevent.isAutoRepeat():
            for (key, trigger: str) in self.keys_pressed:
                if keyevent.text() == key:
                    self.on_trigger(trigger)
                
    def keyReleaseEvent(self, keyevent):
        for (key, trigger: str) in self.keys_released:
            if keyevent.text() == key:
                self.on_trigger(trigger)
    
   
#feather = MCUInterface("/dev/ttyACM0", )        
#Window2 = MainWindow(feather)
#Window2.setupui()


# def update_serial():
#    while True:
#        ser_bytes = ser.readline()
#        decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
#        sertext.appendPlainText("eeee")
#        print(decoded_bytes)

    



#sys.exit(app.exec_())



    

