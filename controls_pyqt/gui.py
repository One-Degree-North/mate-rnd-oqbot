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
        self.camera_number = 2
        self.current_camera = list(range(self.camera_number))
        self.sidebar_shown = True

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
	    background: rgb(42, 46, 50)
        }
        """

    def get_app(self):
        return self.app

    @pyqtSlot()
    def __update_text(self):
        self.timenow = datetime.now()
        self.timepassed = time.time() - self.starttime
        self.voltage_info.setText(str(0.5 * self.mcu.latest_voltage))
        self.timepassedlabel.setText("{:.4f}".format(self.timepassed))
        self.x_gyro.setText("{:.4f}".format(self.mcu.latest_orientation[self.X_INDEX]))
        self.y_gyro.setText("{:.4f}".format(self.mcu.latest_orientation[self.Y_INDEX]))
        self.z_gyro.setText("{:.4f}".format(self.mcu.latest_orientation[self.Z_INDEX]))

        self.x_accel.setText("{:.4f}".format(self.mcu.latest_accel[self.X_INDEX]))
        self.y_accel.setText("{:.4f}".format(self.mcu.latest_accel[self.Y_INDEX]))
        self.z_accel.setText("{:.4f}".format(self.mcu.latest_accel[self.Z_INDEX]))

        self.temperature.setText(str(self.mcu.latest_temp))

        self.imu_compensation.setText(str(self.comms.imu.thread_enable))

        self.thruster1.setText(
            f"{self.mcu.latest_motor_status.motors[MOTOR_LEFT]} -> {self.comms.state.motors[MOTOR_LEFT]}")
        self.thruster2.setText(
            f"{self.mcu.latest_motor_status.motors[MOTOR_RIGHT]} -> {self.comms.state.motors[MOTOR_RIGHT]}")
        self.thruster3.setText(
            f"{self.mcu.latest_motor_status.motors[MOTOR_FRONT]} -> {self.comms.state.motors[MOTOR_FRONT]}")
        self.thruster4.setText(
            f"{self.mcu.latest_motor_status.motors[MOTOR_BACK]} -> {self.comms.state.motors[MOTOR_BACK]}")
        self.servo.setText(str(self.mcu.latest_motor_status.servo))

        # self.update()

    def __create_window(self):
        self.TITLE: str = 'MATE R&D 2021 Control Program - PyQt5 Version'
        self.X_POSITION: int = 0
        self.Y_POSITION: int = 0
        self.LENGTH: int = 1600
        self.WIDTH: int = 800

        # self.setWindowTitle(self.TITLE)
        # self.setGeometry(self.X_POSITION, self.Y_POSITION, self.LENGTH, self.WIDTH)
        # self.show()
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

        self.imu_compensation = QT.QLabel()

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
        self.imu_list.addRow(QT.QLabel("IMU Compensation: "), self.imu_compensation)

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
        self.camera_layout = QT.QHBoxLayout()
        self.camera = [QTM.QCamera(str.encode("/dev/video" + str(x))) for x in range(self.camera_number)]
        self.camera_view = [QTMW.QCameraViewfinder() for x in range(self.camera_number)]
        self.camera_capture = [QTM.QCameraImageCapture(self.camera[x]) for x in range(self.camera_number)]
        self.camera_view_settings = [QTM.QCameraViewfinderSettings() for x in range(self.camera_number)]
        # self.camera_view_settings[1].setResolution(800, 600)

        for x in range(self.camera_number):
            self.camera[x].setViewfinder(self.camera_view[x])
            self.camera[x].setCaptureMode(QTM.QCamera.CaptureStillImage)
            self.camera[x].setViewfinderSettings(self.camera_view_settings[x])
            self.camera_capture[x].setCaptureDestination(QTM.QCameraImageCapture.CaptureToFile)
            self.camera[x].start()
            self.camera_layout.addWidget(self.camera_view[x])

        self.camera_box = QT.QWidget()
        self.camera_box.setLayout(self.camera_layout)

    def __capture_camera(self, camera: int):
        self.camera[camera].searchAndLock()
        self.camera_capture[camera].capture(self.workingdir + "/Camera" + str(camera) + self.timenow.strftime(
            "%d-%m-%y %H:%M:%S-%f"))  # <-file location goes as argument, saves to photos for now
        self.camera[camera].unlock()

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

    def switch_camera(self):
        if self.current_camera[0] == (
                self.camera_number - 1):  # If the first camera in the list is the last camera reset it to show all cameras
            self.current_camera = list(range(self.camera_number))
        elif len(self.current_camera) > 1:  # If 2 or more cameras are shown, only show the first caera in that list
            self.current_camera = [self.current_camera[0]]
        else:  # Else take the frist camera in the list and add one
            self.current_camera = [self.current_camera[0] + 1]

        for x in range(self.camera_number):  # Hides all cameras
            self.camera_view[x].hide()
        for x in self.current_camera:  # Shows all cameras in the current_camera list
            self.camera_view[x].show()

    def hide_sidebar(self):
        if self.sidebar_shown:
            self.general_box.hide()
            self.imu_box.hide()
            self.pwmbox.hide()
            self.layout.setColumnMinimumWidth(4, 0)
            self.sidebar_shown = False
        else:
            self.general_box.show()
            self.imu_box.show()
            self.pwmbox.show()
            self.layout.setColumnMinimumWidth(4, 500)
            self.sidebar_shown = True

    def on_trigger(self, trigger: QKeyEvent, pressed: bool):
        self.comms.read_send(KeySignal(trigger.key(), trigger.text(), pressed))

    def keyPressEvent(self, key_event: QKeyEvent):
        if key_event.isAutoRepeat():
            return

        if key_event.key() == Qt.Key_Escape:
            self.exit_program.exit()
        elif key_event.key() == Qt.Key_Comma:
            self.__capture_camera(self.current_camera[0])
        elif key_event.key() == Qt.Key_Return:
            self.starttime = time.time()
        elif key_event.key() == Qt.Key_P:
            self.switch_camera()
        elif key_event.key() == Qt.Key_O:
            self.hide_sidebar()
        else:
            self.on_trigger(key_event, True)

    def keyReleaseEvent(self, key_event: QKeyEvent):
        if key_event.isAutoRepeat():
            return
        self.on_trigger(key_event, False)

    def closeEvent(self, QCloseEvent):
        self.exit_program.exit()
