# gui.py
# Uses PyQt to collect camera footage and display information from Microcontroller
# Uses PyQt to collect keyboard input too

import sys
from typing import List

from PyQt5.QtCore import Qt, QTimer
import PyQt5.QtMultimedia as QTM
import PyQt5.QtMultimediaWidgets as QTMW
import PyQt5.QtWidgets as QT
from PyQt5.QtGui import QKeyEvent

from mcu_lib.mcu import MCUInterface
from comms import Communications
from controls_pyqt.exit_program import ExitProgram

app = QT.QApplication(sys.argv)


class MainWindow(QT.QWidget):
    def __init__(self, mcu_object: MCUInterface, comms: Communications, exit_program: ExitProgram):
        super().__init__()
        self.timer = QTimer()
        self.TIMEOUT_INTERVAL = 100
        self.ser_text = QT.QPlainTextEdit("text")
        self.mcu: MCUInterface = mcu_object
        self.comms: Communications = comms
        self.exit_program: ExitProgram = exit_program

        self.NUM_THRUSTERS = 4
        self.thruster_speed: List[int] = [0] * self.NUM_THRUSTERS
        self.servo_speed: int = 0

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
            ("I", "li"),
            ("i", "i"),
            ("K", "lk"),
            ("k", "k"),
            ("f", "f"),
            ("F", "f"),
            (" ", "spacebar")
        ]

        self.KEYS_RELEASED = [
            ("w", "sw"),
            ("a", "sa"),
            ("s", "ss"),
            ("d", "sd"),
            ("e", "se"),
            ("q", "sq"),
            ("i", "si"),
            ("k", "sk")
        ]

    def __update_text(self):
        (self.X_INDEX, self.Y_INDEX, self.Z_INDEX) = (0, 1, 2)
        self.thruster1speed, self.thruster2speed, self.thruster3speed, self.thruster4speed = self.thruster_speed

        self.voltage_info.setText(str(self.mcu.latest_voltage))

        self.x_gyro.setText(str(self.mcu.latest_gyro[self.X_INDEX]))
        self.y_gyro.setText(str(self.mcu.latest_gyro[self.Y_INDEX]))
        self.z_gyro.setText(str(self.mcu.latest_gyro[self.Z_INDEX]))

        self.x_accel.setText(str(self.mcu.latest_accel[self.X_INDEX]))
        self.y_accel.setText(str(self.mcu.latest_accel[self.Y_INDEX]))
        self.z_accel.setText(str(self.mcu.latest_accel[self.Z_INDEX]))

        self.temperature.setText(str(self.mcu.latest_temp))

        self.thruster1.setText(str(self.thruster_speed[0]))
        self.thruster2.setText(str(self.thruster_speed[1]))
        self.thruster3.setText(str(self.thruster_speed[2]))
        self.thruster4.setText(str(self.thruster_speed[3]))
        self.servo.setText(str(self.servo_speed))

    def __create_window(self):
        self.TITLE: str = 'MATE'
        self.X_POSITION: int = 0
        self.Y_POSITION: int = 0
        self.LENGTH: int = 1600
        self.WIDTH: int = 800

        self.setWindowTitle(self.TITLE)
        self.setGeometry(self.X_POSITION, self.Y_POSITION, self.LENGTH, self.WIDTH)
        self.show()

    def __initialize_as_label(self):
        self.voltage_info = QT.QLabel()

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

        self.pwm_list.addRow(QT.QLabel("Thruster 1:"), self.thruster1)
        self.pwm_list.addRow(QT.QLabel("Thruster 2:"), self.thruster2)
        self.pwm_list.addRow(QT.QLabel("Thruster 3:"), self.thruster3)
        self.pwm_list.addRow(QT.QLabel("Thruster 4:"), self.thruster4)
        self.pwm_list.addRow(QT.QLabel("Servo:"), self.servo)

        self.pwmbox = QT.QGroupBox("PWM")
        self.pwmbox.setLayout(self.pwm_list)

    def __setup_camera(self):
        self.camera = QTM.QCamera()
        self.camera_view = QTMW.QCameraViewfinder()
        self.camera.setViewfinder(self.camera_view)
        self.camera.setCaptureMode(QTM.QCamera.CaptureViewfinder)
        self.camera.start()

    def __initialize_layout(self):
        self.layout = QT.QGridLayout()
        self.layout.addWidget(self.camera_view, 1, 1, 4, 2)
        self.layout.addWidget(self.general_box, 1, 4, 1, 1)
        self.layout.addWidget(self.imu_box, 2, 4, 1, 1)
        self.layout.addWidget(self.pwmbox, 3, 4, 1, 1)
        self.layout.addWidget(self.ser_text, 1, 3, 4, 1)
        self.layout.setColumnMinimumWidth(3, 400)
        self.layout.setColumnMinimumWidth(4, 300)
        self.setLayout(self.layout)

    def setup_ui(self):
        self.__create_window()
        self.__initialize_as_labels()

        self.__initialize_general_info()
        self.__initialize_imu_list()
        self.__initialize_pwm_list()

        self.comms.start_elec_ops()

        self.__setup_camera()

        self.ser_text.setReadOnly(True)

        self.__initialize_layout()

        self.timer.timeout.connect(self.__update_text)
        self.timer.start(self.TIMEOUT_INTERVAL)

    def on_trigger(self, trigger: str):
        self.comms.read_send(trigger)

    def keyPressEvent(self, key_event: QKeyEvent):
        if key_event.key() == Qt.Key_Escape:
            self.exit_program.Exit()

        if not key_event.isAutoRepeat():
            for (key, trigger) in self.KEYS_PRESSED:
                print(key, trigger)
                if key_event.text() == key:
                    self.on_trigger(trigger)

    def keyReleaseEvent(self, keyevent):
        if not keyevent.isAutoRepeat():
            for (key, trigger) in self.KEYS_RELEASED:
                if keyevent.text().lower() == key:
                    self.on_trigger(trigger)

    def closeEvent(self, QCloseEvent):
        self.exit_program.Exit()
