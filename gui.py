import sys
from PyQt5.QtCore import Qt
import PyQt5.QtMultimedia as QTM
import PyQt5.QtMultimediaWidgets as QTMW
import PyQt5.QtWidgets as QT



app = QT.QApplication(sys.argv)
window = QT.QWidget()

window.setWindowTitle('MATE')
window.setGeometry(0, 0, 800, 40)
window.show()

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

Camera = QTM.QCamera()
CameraView = QTMW.QCameraViewfinder()
CameraView.show()
Camera.setViewfinder(CameraView)
Camera.setCaptureMode(QTM.QCamera.CaptureViewfinder)
Camera.start()

layout = QT.QGridLayout()

layout.addWidget(QT.QLabel("Camera"),1,1)
layout.addWidget(IMUBox,1,2)
layout.addWidget(CameraView,1,3)

window.setLayout(layout)

sys.exit(app.exec_())
