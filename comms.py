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
    MULTIPLIER_PERCENT = 2
    
    def __init__(self, mcuVAR: MCUInterface):
        self.mcuVAR = mcuVAR
        pass
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
            
            "e" = MOTOR_CLAW,
            "d" = MOTOR_RIGHT,
            "w" = MOTOR_FRONT,
            "a" = MOTOR_LEFT,
            "s" = MOTOR_BACKWARD
            
        }
       
       for command in dict_motors.keys():
            if key_pressed[-1] == command:
                if len(key_pressed) == 1:
                    self.mcuVAR.cmd_setMotorCalibrated(dict_motors.get(command), INITIAL_PERCENT)
                elif key_pressed[0] == "s":
                    self.mcuVAR.cmd_setMotorCalibrated(dict_motors.get(command), MULTIPLIER_PERCENT)
                elif key_pressed[0] == "l":
                    self.mcuVAR.cmd_setMotorCalibrated(dict_motors.get(command), -1*MULTIPLIER_PERCENT)
                        
    def kill_elec_ops():
        
        self.mcuVAR.cmd_halt()
        self.mcuVAR.setAutoReport(PARAM_ACCEL, false, 0)
        self.mcuVAR.setAutoReport(PARAM_GYRO, false, 0)
        self.mcuVAR.setAutoReport(PARAM_VOLT_TEMP, false, 0)
        self.mcuVAR.close_serial()


