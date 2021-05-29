import sys
from PyQt5.QtCore import Qt
import PyQt5.QtMultimedia as QTM
import PyQt5.QtMultimediaWidgets as QTMW
import PyQt5.QtWidgets as QT

app = QT.QApplication(sys.argv)
window = QT.QWidget()

window.setWindowTitle('MATE')
window.setGeometry(0, 0, 1200, 800)
window.show()


Generallist = QT.QFormLayout()

voltageinfo = QT.QLabel()
voltageinfo.setText("2")
Generallist.addRow(QT.QLabel("Voltage:"),voltageinfo)

GeneralBox = QT.QGroupBox("General")
GeneralBox.setLayout(Generallist)


IMUlist = QT.QFormLayout()

xgyro = QT.QLabel()
ygyro = QT.QLabel()
zgyro = QT.QLabel()
xaccel = QT.QLabel()
yaccel = QT.QLabel()
zaccel = QT.QLabel()
temperature = QT.QLabel()

xgyro.setText(str(99.233))
ygyro.setText(str(99.231))
zgyro.setText(str(99.283))
xaccel.setText(str(99.233))
yaccel.setText(str(99.231))
zaccel.setText(str(99.283))
temperature.setText(str(99.283))

IMUlist.addRow(QT.QLabel("X Rotation:"),xgyro)
IMUlist.addRow(QT.QLabel("Y Rotation:"),ygyro)
IMUlist.addRow(QT.QLabel("Z Rotation:"),zgyro)
IMUlist.addRow(QT.QLabel("X Accerleration:"),xaccel)
IMUlist.addRow(QT.QLabel("Y Accerleration:"),yaccel)
IMUlist.addRow(QT.QLabel("Z Accerleration:"),zaccel)
IMUlist.addRow(QT.QLabel("Temperature:"),temperature)

IMUBox = QT.QGroupBox("IMU")
IMUBox.setLayout(IMUlist)


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


serial = QT.QPlainTextEdit("text")
serial.setReadOnly(True)

layout = QT.QGridLayout()



layout.addWidget(CameraView,1,1,4,2)
layout.addWidget(GeneralBox,1,3,1,1)
layout.addWidget(IMUBox,2,3,1,1)
layout.addWidget(PWMBox,3,3,1,1)
layout.addWidget(serial,1,4,4,1)



window.setLayout(layout)

sys.exit(app.exec_())
