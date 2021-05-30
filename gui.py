import sys
import threading
import serial
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
import PyQt5.QtMultimedia as QTM
import PyQt5.QtMultimediaWidgets as QTMW
import PyQt5.QtWidgets as QT

ser = serial.Serial('/dev/ttyACM0')
ser.flushInput()

app = QT.QApplication(sys.argv)
window = QT.QWidget()

window.setWindowTitle('MATE')
window.setGeometry(0, 0, 1600, 800)
window.show()


Generallist = QT.QFormLayout()

voltageinfo = QT.QLabel()
voltageinfo.setText("2")
Generallist.addRow(QT.QLabel("Voltage:"),voltageinfo)

GeneralBox = QT.QGroupBox("General")
GeneralBox.setLayout(Generallist)


IMU_list = QT.QFormLayout()

x_gyro = QT.QLabel()
y_gyro = QT.QLabel()
z_gyro = QT.QLabel()
x_accel = QT.QLabel()
y_accel = QT.QLabel()
z_accel = QT.QLabel()
temperature = QT.QLabel()

x_gyro.setText(str(99.233))
y_gyro.setText(str(99.231))
z_gyro.setText(str(99.283))
x_accel.setText(str(99.233))
y_accel.setText(str(99.231))
z_accel.setText(str(99.283))
temperature.setText(str(99.283))

IMU_list.addRow(QT.QLabel("X Rotation:"),x_gyro)
IMU_list.addRow(QT.QLabel("Y Rotation:"),y_gyro)
IMU_list.addRow(QT.QLabel("Z Rotation:"),z_gyro)
IMU_list.addRow(QT.QLabel("X Accerleration:"),x_accel)
IMU_list.addRow(QT.QLabel("Y Accerleration:"),y_accel)
IMU_list.addRow(QT.QLabel("Z Accerleration:"),z_accel)
IMU_list.addRow(QT.QLabel("Temperature:"),temperature)

IMU_Box = QT.QGroupBox("IMU")
IMU_Box.setLayout(IMU_list)


PWMlist = QT.QFormLayout()

Thruster1 = QT.QLabel()
Thruster2 = QT.QLabel()
Thruster3 = QT.QLabel()
Thruster4 = QT.QLabel()
Servo = QT.QLabel()

Thruster1.setText(str(99.231))
Thruster2.setText(str(99.283))
Thruster3.setText(str(99.233))
Thruster4.setText(str(99.231))
Servo.setText(str(99.233))

PWMlist.addRow(QT.QLabel("Thruster 1:"),Thruster1)
PWMlist.addRow(QT.QLabel("Thruster 2:"),Thruster2)
PWMlist.addRow(QT.QLabel("Thruster 3:"),Thruster3)
PWMlist.addRow(QT.QLabel("Thruster 4:"),Thruster4)
PWMlist.addRow(QT.QLabel("Servo:"),Servo)

PWMBox = QT.QGroupBox("PWM")
PWMBox.setLayout(PWMlist)


Camera = QTM.QCamera()
CameraView = QTMW.QCameraViewfinder()
Camera.setViewfinder(CameraView)
Camera.setCaptureMode(QTM.QCamera.CaptureViewfinder)
Camera.start()


sertext = QT.QPlainTextEdit("text")
sertext.setReadOnly(True)


layout = QT.QGridLayout()
layout.addWidget(CameraView,1,1,4,2)
layout.addWidget(GeneralBox,1,4,1,1)
layout.addWidget(IMU_Box,2,4,1,1)
layout.addWidget(PWMBox,3,4,1,1)
layout.addWidget(sertext,1,3,4,1)
layout.setColumnMinimumWidth(3,400)

window.setLayout(layout)

def update_serial():
    while True:
        ser_bytes = ser.readline()
        decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
        sertext.appendPlainText("eeee")
        print(decoded_bytes)

serialthread = QThread()
serialworker = Worker()


sys.exit(app.exec_())



    

