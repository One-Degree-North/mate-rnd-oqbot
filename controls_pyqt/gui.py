# gui.py
# Uses PyQt to collect camera footage and display information from Microcontroller
# Uses PyQt to collect keyboard input too

import os
import sys
from datetime import datetime
import time
from typing import List

from PyQt5.QtCore import Qt, QTimer, pyqtSlot
import PyQt5.QtMultimedia as QTM
import PyQt5.QtMultimediaWidgets as QTMW
import PyQt5.QtWidgets as QT
from PyQt5.QtGui import QKeyEvent

from mcu_lib.mcu import MCUInterface
from mcu_lib.command_constants import *
from comms import Communications
from controls_pyqt.exit_program import ExitProgram
from controls_pyqt.key_signal import KeySignal


class MainWindow(QT.QWidget):
    def __init__(self, mcu_object: MCUInterface, comms: Communications, app: QT.QApplication):
        super().__init__()
        self.timer = QTimer()
        self.TIMEOUT_INTERVAL = 100
        self.ser_text = QT.QPlainTextEdit("text")
        self.workingdir = os.path.dirname(os.path.realpath(__file__))
        self.timenow = datetime.now()
        self.starttime = time.time()
        self.mcu: MCUInterface = mcu_object
        self.comms: Communications = comms
        self.app = app
        self.exit_program: ExitProgram = ExitProgram(self.comms)
        self.NUM_THRUSTERS = 4
        self.thruster_speed: List[int] = [0] * self.NUM_THRUSTERS
        self.servo_speed: int = 0
        (self.X_INDEX, self.Y_INDEX, self.Z_INDEX) = (0, 1, 2)

        # (key, message sent to comms)
        self.KEYS = [
            "q", "w", "e", "a", "s", "d", "f", "g", "h", "z", "x", "c", "i", "j", "k", "l", "1", "2", "3", "4", "0", "7"
        ]
        
        self.fourk_stylesheet = """
        QLabel {
            font-size: 40px;
            color: white
        }
        QGroupBox { 
            font-size: 50px; 
            font-weight: bold;
            border-radius: 10px;
            border: 2px solid lightGrey;
            margin-top: 1ex;
            padding: 30px
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            padding-bottom:0 30px;
            padding-top:0 30px;
            left: 20px;
            color: white
        }
	QWidget {
	    background: black
        }
        """

    def get_app(self):
        return self.app

    @pyqtSlot()
    def __update_text(self):
        self.timenow = datetime.now
        self.timepassed = time.time() - self.starttime
        self.voltage_info.setText(str(self.mcu.latest_voltage))
        self.timepassedlabel.setText(str(self.timepassed))
        self.x_gyro.setText("{:.4f}".format(self.mcu.latest_gyro[self.X_INDEX]))
        self.y_gyro.setText("{:.4f}".format(self.mcu.latest_gyro[self.Y_INDEX]))
        self.z_gyro.setText("{:.4f}".format(self.mcu.latest_gyro[self.Z_INDEX]))

        self.x_accel.setText("{:.4f}".format(self.mcu.latest_accel[self.X_INDEX]))
        self.y_accel.setText("{:.4f}".format(self.mcu.latest_accel[self.Y_INDEX]))
        self.z_accel.setText("{:.4f}".format(self.mcu.latest_accel[self.Z_INDEX]))

        self.temperature.setText(str(self.mcu.latest_temp))

        self.thruster1.setText(str(self.mcu.latest_motor_status.motors[MOTOR_LEFT]))
        self.thruster2.setText(str(self.mcu.latest_motor_status.motors[MOTOR_RIGHT]))
        self.thruster3.setText(str(self.mcu.latest_motor_status.motors[MOTOR_FRONT]))
        self.thruster4.setText(str(self.mcu.latest_motor_status.motors[MOTOR_BACK]))
        self.servo.setText(str(self.mcu.latest_motor_status.servo))

        # self.update()

    def __create_window(self):
        self.TITLE: str = 'MATE'
        self.X_POSITION: int = 0
        self.Y_POSITION: int = 0
        self.LENGTH: int = 1600
        self.WIDTH: int = 800

        #self.setWindowTitle(self.TITLE)
        #self.setGeometry(self.X_POSITION, self.Y_POSITION, self.LENGTH, self.WIDTH)
        #self.show()
        self.showFullScreen()

    def __initialize_as_labels(self):
        self.voltage_info = QT.QLabel()
        self.timepassedlabel = QT.QLabel()
        
        self.x_gyro = QT.QLabel()
        self.y_gyro = QT.QLabel()
        self.z_gyro = QT.QLabel()

        self.x_accel = QT.QLabel()
        self.y_accel = QT.QLabel()
        self.z_accel = QT.QLabel()

        self.temperature = QT.QLabel()

        self.thruster1 = QT.QLabel()
        self.thruster2 = QT.QLabel()
        self.thruster3 = QT.QLabel()
        self.thruster4 = QT.QLabel()
        self.servo = QT.QLabel()

    def __initialize_general_info(self):
        self.general_list = QT.QFormLayout()
        self.general_list.addRow(QT.QLabel("Voltage:"), self.voltage_info)
        self.general_list.addRow(QT.QLabel("Time Passed:"), self.timepassedlabel)
        self.general_box = QT.QGroupBox("General")
        self.general_box.setLayout(self.general_list)

    def __initialize_imu_list(self):
        self.imu_list = QT.QFormLayout()

        self.imu_list.addRow(QT.QLabel("X Rotation:"), self.x_gyro)
        self.imu_list.addRow(QT.QLabel("Y Rotation:"), self.y_gyro)
        self.imu_list.addRow(QT.QLabel("Z Rotation:"), self.z_gyro)
        self.imu_list.addRow(QT.QLabel("X Acceleration:"), self.x_accel)
        self.imu_list.addRow(QT.QLabel("Y Acceleration:"), self.y_accel)
        self.imu_list.addRow(QT.QLabel("Z Acceleration:"), self.z_accel)
        self.imu_list.addRow(QT.QLabel("Temperature:"), self.temperature)

        self.imu_box = QT.QGroupBox("IMU")
        self.imu_box.setLayout(self.imu_list)

    def __initialize_pwm_list(self):
        self.pwm_list = QT.QFormLayout()

        self.pwm_list.addRow(QT.QLabel("Left Thruster:"), self.thruster1)
        self.pwm_list.addRow(QT.QLabel("Right Thruster:"), self.thruster2)
        self.pwm_list.addRow(QT.QLabel("Front Thruster:"), self.thruster3)
        self.pwm_list.addRow(QT.QLabel("Back Thruster:"), self.thruster4)
        self.pwm_list.addRow(QT.QLabel("Claw:"), self.servo)

        self.pwmbox = QT.QGroupBox("PWM")
        self.pwmbox.setLayout(self.pwm_list)

    def __setup_camera(self):
        self.camera_layout = QT.QVBoxLayout()
        
        self.camera = QTM.QCamera(str.encode("/dev/video0"))
        self.camera_view = QTMW.QCameraViewfinder()
        self.camera.setViewfinder(self.camera_view)
        self.camera_capture = QTM.QCameraImageCapture(self.camera)
        self.camera.setCaptureMode(QTM.QCamera.CaptureStillImage)
        self.camera_capture.setCaptureDestination(QTM.QCameraImageCapture.CaptureToFile)
        self.camera.start()
        
        self.capture_button = QT.QPushButton("Capture")

        self.camera2 = QTM.QCamera(str.encode("/dev/video1"))
        self.camera_view2 = QTMW.QCameraViewfinder()
        self.camera2.setViewfinder(self.camera_view2)
        self.camera2_capture = QTM.QCameraImageCapture(self.camera2)
        self.camera2.setCaptureMode(QTM.QCamera.CaptureStillImage)
        self.camera2_capture.setCaptureDestination(QTM.QCameraImageCapture.CaptureToFile)
        self.camera2.start()
        
        self.capture_button2 = QT.QPushButton("Capture")
       
        self.camera_layout.addWidget(self.camera_view)
        self.camera_layout.addWidget(self.capture_button)
        self.camera_layout.addWidget(self.camera_view2)
        self.camera_layout.addWidget(self.capture_button2)
        
        self.camera_box = QT.QWidget()
        self.camera_box.setLayout(self.camera_layout)
        
        self.capture_button.clicked.connect(self.__capture_camera)
        self.capture_button2.clicked.connect(self.__capture_camera2)
    
    def __capture_camera(self):
        self.camera.searchAndLock()
        self.camera_capture.capture(self.workingdir + "/Camera 1 " + self.timenow.strftime("%d-%m-%y %H:%M:%S-%f"))  # <-file location goes as argument, saves to photos for now
        self.camera.unlock()
        
    def __capture_camera2(self):
        self.camera2.searchAndLock()
        self.camera2_capture.capture(self.workingdir + "/Camera 2 " + self.timenow.strftime("%d-%m-%y %H:%M:%S-%f"))  # <-file location goes as argument, saves to photos for now
        self.camera2.unlock()
        
    def __initialize_layout(self):
        self.layout = QT.QGridLayout()
        self.layout.addWidget(self.camera_box, 1, 1, 3, 1)
        self.layout.addWidget(self.general_box, 1, 4, 1, 1)
        self.layout.addWidget(self.imu_box, 2, 4, 1, 1)
        self.layout.addWidget(self.pwmbox, 3, 4, 1, 1)
        # self.layout.addWidget(self.ser_text, 1, 3, 4, 1)
        # self.layout.setColumnMinimumWidth(3, 400)
        self.layout.setColumnMinimumWidth(4, 600)
        self.setLayout(self.layout)

    def setup_ui(self):
        self.__create_window()
        self.__initialize_as_labels()

        self.__initialize_general_info()
        self.__initialize_imu_list()
        self.__initialize_pwm_list()

        self.comms.start_elec_ops()
        self.comms.start_thread()

        self.__setup_camera()

        self.ser_text.setReadOnly(True)

        self.__initialize_layout()
        self.setStyleSheet(self.fourk_stylesheet)
        
        self.timer.timeout.connect(self.__update_text)
        self.timer.start(self.TIMEOUT_INTERVAL)

    def start_ui(self):
        sys.exit(self.app.exec_())

    def on_trigger(self, trigger: str, pressed: bool):
        self.comms.read_send(KeySignal(trigger, pressed))

    def keyPressEvent(self, key_event: QKeyEvent):
        if key_event.key() == Qt.Key_Escape:
            self.exit_program.exit()
        if key_event.key() == Qt.Key_Period:
            self.__capture_camera2()
        if key_event.key() == Qt.Key_Comma:
            self.__capture_camera()
        if key_event.key() == Qt.Key_Space:
            self.on_trigger("e", True)
        if key_event.key() == Qt.Key_Return
            self.starttime = time.time()

        if not key_event.isAutoRepeat():
            for key in self.KEYS:
                if key_event.text().lower() == key:
                    self.on_trigger(key, True)

    def keyReleaseEvent(self, key_event: QKeyEvent):
        if key_event.key() == Qt.Key_Space:
            self.on_trigger("e", False)
        if not key_event.isAutoRepeat():
            for key in self.KEYS:
                if key_event.text().lower() == key:
                    self.on_trigger(key, False)

    def closeEvent(self, QCloseEvent):
        self.exit_program.exit()
