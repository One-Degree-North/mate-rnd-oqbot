# gui.py
# Uses PyQt to collect camera footage and display information from Microcontroller
# Uses PyQt to collect keyboard input too

import random
import sys


from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QTimer, QEvent
import PyQt5.QtMultimedia as QTM
import PyQt5.QtMultimediaWidgets as QTMW
import PyQt5.QtWidgets as QT
from PyQt5.QtGui import QKeyEvent


from mcu import MCUInterface


sys.path.insert(0, './mcu-lib')
app = QT.QApplication(sys.argv)


class MainWindow(QT.QWidget):
    def __init__(self, mcuobject: MCUInterface, comms: Communications, exit_program: ExitProgram):
        super().__init__()
        self.mcu: MCUInterface = mcuobject
        self.thruster1speed: int = 0
        self.thruster2speed: int = 0
        self.thruster3speed: int = 0
        self.thruster4speed: int = 0
        self.servospeed: int = 0
        
        self.comms: Communications = comms
        self.exit_program: ExitProgram = exit_program
        
        # (key, message sent to comms)
        self.KEYS_PRESSED = [
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
        
        self.KEYS_RELEASED = [
            ("w", "sw"),
            ("a", "sa"),
            ("s", "ss"),
            ("d", "sd"),
            ("e", "se"),
            ("q", "sq")
        ]
    
    def __update_text(self):
        self.gyro = self.mcu.latest_gyro
        self.accel = self.mcu.latest_accel
        self.temp = self.latest_temp
        self.voltage = self.mcu.latest_voltage
        (self.X_INDEX, self.Y_INDEX, self.Z_INDEX) = (0, 1, 2)
        
        self.voltage_info.setText(str(self.voltage))
        
        self.x_gyro.setText(str(self.mcu.gyro[self.X_INDEX]))
        self.y_gyro.setText(str(self.mcu.gyro[self.Y_INDEX]))
        self.z_gyro.setText(str(self.mcu.gyro[self.Z_INDEX]))
        
        self.x_accel.setText(str(self.mcu.latest_accel[self.X_INDEX]))
        self.y_accel.setText(str(self.mcu.latest_accel[self.Y_INDEX]))
        self.z_accel.setText(str(self.mcu.latest_accel[self.Z_INDEX]))
        
        self.temperature.setText(str(self.temp))
        
        self.thruster1.setText(str(self.thruster1speed))
        self.thruster2.setText(str(self.thruster2speed))
        self.thruster3.setText(str(self.thruster3speed))
        self.thruster4.setText(str(self.thruster4speed))
        self.servo.setText(str(self.servospeed))
    
    def setup_ui(self):
        self.TITLE: str = 'MATE'
        self.X_POSITION: int = 0
        self.Y_POSITION: int = 0
        self.LENGTH: int = 1600
        self.WIDTH: int = 800
        
        self.setWindowTitle(self.TITLE)
        self.setGeometry(self.X_POSITION, self.Y_POSITION, self.LENGTH, self.WIDTH)
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
        
        TIMEOUT_INTERVAL = 100
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.__update_text)
        self.timer.start(TIMEOUT_INTERVAL)
    
    def on_trigger(self, trigger: str):
        self.comms.read_send(trigger)
    
    def keyPressEvent(self, keyevent):
        if keyevent.key() == Qt.Key_Escape:
            self.exit_program.Exit()
        
        if not keyevent.isAutoRepeat():
            for (key, trigger: str) in self.KEYS_PRESSED:
                if keyevent.text() == key:
                    self.on_trigger(trigger)
                
    def keyReleaseEvent(self, keyevent):
        if not keyevent.isAutoRepeat():
            for (key, trigger: str) in self.KEYS_RELEASAED:
                if keyevent.text() == key:
                    self.on_trigger(trigger)
                    
    def closeEvent(self, QCloseEvent):
        self.exit_program.Exit()
