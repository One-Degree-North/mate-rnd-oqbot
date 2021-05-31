import sys
import threading
import serial
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QTimer
import PyQt5.QtMultimedia as QTM
import PyQt5.QtMultimediaWidgets as QTMW
import PyQt5.QtWidgets as QT


ser = serial.Serial('/dev/ttyACM0')
ser.flushInput()

app = QT.QApplication(sys.argv)


#    def run(self):
#        self.ser_bytes = ser.readline()
#        self.decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
#        MainWindow.sertext.appendPlainText(decoded_bytes)
#        print(self.decoded_bytes)

class mcuthing:
    voltage = 2
    gyrox = 99
    gyroy = 12
    gyroz = 43
    accelx = 92
    accely = 32
    accelz = 93
    temperature = 121


class MainWindow(QT.QWidget):
    def __init__(self, mcuobject):
        super().__init__()
        self.mcu = mcuobject
    
    def updatetext(self):
        self.voltage_info.setText(str(self.mcu.voltage))
        self.x_gyro.setText(str(self.mcu.gyrox))
        self.y_gyro.setText(str(self.mcu.gyroy))
        self.z_gyro.setText(str(self.mcu.gyroz))
        
    def setupui(self):
        self.setWindowTitle('MATE')
        self.setGeometry(0, 0, 1600, 800)
        self.show()
        
        self.general_list = QT.QFormLayout()
        self.voltage_info = QT.QLabel()
        self.voltage_info.setText("2")
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
        self.x_gyro.setText(str(99.233))
        self.y_gyro.setText(str(99.231))
        self.z_gyro.setText(str(99.283))
        self.x_accel.setText(str(99.233))
        self.y_accel.setText(str(99.231))
        self.z_accel.setText(str(99.283))
        self.temperature.setText(str(99.283))
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
        self.thruster1.setText(str(99.231))
        self.thruster2.setText(str(99.283))
        self.thruster3.setText(str(99.233))
        self.thruster4.setText(str(99.231))
        self.servo.setText(str(99.233))
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
        self.setLayout(self.layout)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.updatetext)
        self.timer.start(100)
    
        
feather = mcuthing()        
Window2 = MainWindow(feather)
Window2.setupui()

# def update_serial():
#    while True:
#        ser_bytes = ser.readline()
#        decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
#        sertext.appendPlainText("eeee")
#        print(decoded_bytes)

    




sys.exit(app.exec_())



    

