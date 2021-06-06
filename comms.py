from mcu import *

class Communications:
    
    PWM_MIN = 1000
    PWM_MID = 1500
    PWM_MAX = 2000
    
    MOTOR_CLAW = 0 
    MOTOR_FRONT = 1
    MOTOR_RIGHT = 2
    MOTOR_LEFT = 3 
    MOTOR_BACK = 4
    
    INITIAL_PERCENT = 100
    
    def __init__(self, mcuVAR: MCUInterface, MULTIPLIER_PERCENT: int):
        self.mcuVAR = mcuVAR
        self.MULTIPLIER_PERCENT = MULTIPLIER_PERCENT
    
    def read_send(key_pressed):
        
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_CLAW,1000)
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_FRONT, 1000)
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_LEFT, 1000)
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_RIGHT, 1000)
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_BACK, 1000)

        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_CLAW, PWM_MID)
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_FRONT, PWM_MID)
        self.mcuVAR.cmd_setMotorMicroseconds(MOTOR_LEFT, PWM_MID)
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_RIGHT, PWM_MID)
        self.mcuVAR.cmd_setMotorCalibration(MOTOR_BACK, PWM_MID)

        
        dict_motors = {
            "e": [MOTOR_FRONT, MOTOR_BACK],
            "q": [MOTOR_BACK, MOTOR_FRONT],
            "d": right, #Which motors move for this?
            "a": left,  #Which motors move for this?
            "w": [MOTOR_LEFT, MOTOR_RIGHT],
            "s": [MOTOR_RIGHT, MOTOR_LEFT] 
        }
        
        spacebar_count = 0

        if key_pressed[0] == "s" and len(key_pressed)==2:
            for motor in range(0, len(dict_motors[key_pressed[1]])):
                self.mcuVAR.cmd_setMotorCalibrated(dict_motors[key_pressed[1]][motor],0)
        elif key_pressed[0] == "l":
            for motor in range(0, len(dict_motors[key_pressed[1]])):
                self.mcuVAR.cmd_setMotorCalibrated(dict_motors[key_pressed[1]][motor],(2*i-1)*MULTIPLIER_PERCENT)
        elif len(key_pressed) == 1:
            for i in range(0, len(dict_motors[key_pressed[1]])):
                self.mcuVAR.cmd_setMotorCalibrated(dict_motors[key_pressed[1]][i],(2*i-1)*INITIAL_PERCENT)
        elif key_pressed =="spacebar":
            spacebar_count+=1
            if spacebar_count%3 == 1:
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_CLAW,INITIAL_PERCENT)
            elif spacebar_count%3 == 2:
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_CLAW,0)
            elif spacebar_count%3 == 0:
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_CLAW,-1*INITIAL_PERCENT)
                
                        
    def kill_elec_ops():
        
        self.mcuVAR.cmd_halt()
        self.mcuVAR.setAutoReport(PARAM_ACCEL, false, 0)
        self.mcuVAR.setAutoReport(PARAM_GYRO, false, 0)
        self.mcuVAR.setAutoReport(PARAM_VOLT_TEMP, false, 0)
        self.mcuVAR.close_serial()


 '''
         
         If it only starts to close after pressing the third time?
         
         elif key_pressed =="spacebar":
            spacebar_count+=1
            if spacebar_count%4 == 1:
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_CLAW,INITIAL_PERCENT)
            elif spacebar_count%3 == 2:
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_CLAW,0)
            elif spacebar_count%3 == 3:
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_CLAW,-1*INITIAL_PERCENT)
            elif spacebar_count%3 == 0:
                self.mcuVAR.cmd_setMotorCalibrated(MOTOR_CLAW,-1*INITIAL_PERCENT)
 '''    
        
