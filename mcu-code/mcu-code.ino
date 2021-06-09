/* microcontroller-side code for MATE R&D OQBot
** refer to docs/packet-structure and docs/command-list for more details
** status:
** all commands are implemented but untested.
 */


// --------------- SECTION: DEFINITIONS --------------- //

#include <Adafruit_ICM20649.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <Servo.h>

#define VERSION 0

// define debug
// #define Debug_Serial Serial
// #define DEBUG_BAUDRATE 230400

// enable debug
// #define DEBUG
// #define Debug(a) (Serial.print(a))
// #define Debugln(a) (Serial.println(a))
// #define VERBOSE

// disable debug
#define Debug(a)
#define Debugln(a)

// define communications
#define Comms Serial1
#define COMMS_BAUDRATE 230400

// define motor details
#define PWM_MIN 1000
#define PWM_MID 1500
#define PWM_MAX 2000
#define NUM_MOTORS 5
byte pins[] = {A4, A5, 9, 10, 11};
uint16_t calibration[] = {1000, 1000, 1000, 1000, 1000};
Servo motors[NUM_MOTORS];

// define voltage calibrations
#define VOLTAGE_PIN A2
#define R1 2000
#define R2 390
float voltage_calibration = 7.55;

// create sensor objects
Adafruit_ICM20649 icm;
sensors_event_t icmAccel;
sensors_event_t icmGyro;
sensors_event_t icmTemp;

// values for settings
boolean enableFeedback = true;
boolean enableAutoReport[] = {false, false, false};
uint16_t autoReportDelay[] = {100, 100, 100};
unsigned long autoReportTimers[] = {0, 0, 0};

// --------------- SECTION: INITIALIZATION --------------- //

void initSerial() {
  #ifdef DEBUG
  Debug_Serial.begin(DEBUG_BAUDRATE);
  #endif
  Comms.begin(COMMS_BAUDRATE);
  delay(200);
  Debugln("initSerial: Serial Init complete");
}

void setDefaultRanges(){
  icm.setAccelRange(ICM20649_ACCEL_RANGE_16_G);
  icm.setGyroRange(ICM20649_GYRO_RANGE_500_DPS);
  icm.setAccelRateDivisor(15); 
  icm.setGyroRateDivisor(15);
  Debugln("setDefaultRanges: ICM20649 default ranges set.");
}

void initSensors() {
  if (!icm.begin_I2C()){
    Debugln("initSensors: ICM20649 Init over I2C failed.");
    while(true){
      delay(10);
    }
  }
  Debugln("initSensors: ICM20649 Init complete");
  setDefaultRanges();
}

void initMotors() {
  for (int i = 0; i < NUM_MOTORS; i++){
    motors[i].attach(pins[i]); 
    Debug("initMotors: motor ");
    Debug(i);
    Debug(" attached to pin ");
    Debugln(pins[i]);
  }
  Debugln("initMotors: Motor Init complete");
}

void setup() {
  digitalWrite(8, HIGH);
  initSerial();
  initSensors();
  initMotors();
}

// --------------- SECTION: HELPER FUNCTIONS --------------- //

float getVoltage(int rawInput){
  return (rawInput / 1024.0) * (R1 + R2) / R2 * voltage_calibration;
}

uint16_t percentToMicroseconds(int8_t percent){
  if (percent < -100 || percent > 100) { return PWM_MID; }
  if (percent >= 0){
    return PWM_MID + (uint16_t) (percent * (PWM_MAX - PWM_MID) / 100.0);
  } else {
    return PWM_MID - (uint16_t) (percent * (PWM_MID - PWM_MIN) / 100.0);
  }
}

uint16_t calibrate(byte motor, uint16_t microseconds){
  if (microseconds >= PWM_MID){
    return PWM_MID + min((microseconds - PWM_MID) * calibration[motor] / 1000, PWM_MAX);
  } else {
    return PWM_MID - max((PWM_MID - microseconds) * calibration[motor] / 1000, PWM_MIN);
  }
}

void setPWM(byte motor, uint16_t microseconds){
  motors[motor].writeMicroseconds(microseconds);
}

void setPercent(byte motor, int8_t percent){
  setPWM(motor, calibrate(motor, percentToMicroseconds(percent)));
}

void setAccelerometerRange(byte mode){
  Debug("setAccelerometerRange: ");
  if (mode < 0x00 || mode > 0x03){ return; }
  Debugln(mode);
  switch (mode)
  {
    case 0x00:
      icm.setAccelRange(ICM20649_ACCEL_RANGE_4_G);
      break;
    case 0x01:
      icm.setAccelRange(ICM20649_ACCEL_RANGE_8_G);
      break;
    case 0x02:
      icm.setAccelRange(ICM20649_ACCEL_RANGE_16_G);
      break;
    case 0x03:
      icm.setAccelRange(ICM20649_ACCEL_RANGE_30_G);
      break;
    default:
      Debugln("setAccelerometerRange: invalid accelerometer range!");
      break;
  }
}

void setGyroscopeRange(byte mode){
  Debug("setGyroscopeRange: ");
  if (mode < 0x00 || mode > 0x03){ return; }
  Debugln(mode);
  switch (mode)
  {
    case 0x00:
    case '0':
      icm.setGyroRange(ICM20649_GYRO_RANGE_500_DPS);
      break;
    case 0x01:
    case '1':
      icm.setGyroRange(ICM20649_GYRO_RANGE_1000_DPS);
      break;
    case 0x02:
    case '2':
      icm.setGyroRange(ICM20649_GYRO_RANGE_2000_DPS);
      break;
    case 0x03:
    case '3':
      icm.setGyroRange(ICM20649_GYRO_RANGE_4000_DPS);
      break;
    default:
      Debugln("setGyroscopeRange: invalid gyroscope range!");
      break;
  }
}

void setAccelerometerDivisor(byte divisor){
  Debug("setAccelerometerDivisor: ");
  Debugln(divisor);
  icm.setAccelRateDivisor(divisor);
}

void setGyroscopeDivisor(byte divisor){
  Debug("setGyroscopeDivisor: ");
  Debugln(divisor);
  icm.setGyroRateDivisor(divisor);
}

void updateSensors(){
  Debugln("updateSensors: updating sensors");
  icm.getEvent(&icmAccel, &icmGyro, &icmTemp);
}

// --------------- SECTION: SERIAL COMMUNICATION --------------- //

void readSerial(){
  if (Comms.available() >= 8){
    // read Comms until header is received or not enough bytes
    byte header = 0x00;
    while (Comms.available() > 7 && header != 0xCA){
      header = Comms.read();
    } 
    // verify header
    if (header != 0xCA) {
      digitalWrite(8, LOW);
      Debugln("readSerial: packet received, but header did not match.");
      #ifdef VERBOSE
      Debug("header: ");
      Debugln(header);
      #endif
      return; 
    } else {
      digitalWrite(8, HIGH);
    }
    // get the contents of the packet
    byte cmd = Comms.read(); // 0x1
    byte param = Comms.read(); // 0x2
    byte data[4];
    for (int i = 0; i < 4; i++){
      data[i] = Comms.read();
    }
    byte footer = Comms.read();
    // verify footer
    if (footer != 0x47){
      Debugln("readSerial: packet received, but footer did not match.");
      #ifdef VERBOSE
      Debug("packet: ");
      Debug(header);
      Debug(" ");
      Debug(cmd);
      Debug(" ");
      Debug(param);
      Debug(" ");
      Debug(data[0]);
      Debug(" ");
      Debug(data[1]);
      Debug(" ");
      Debug(data[2]);
      Debug(" ");
      Debug(data[3]);
      Debug(" ");
      Debugln(footer);
      #endif
      return;
    }
    // call parseSerial
    parseSerial(cmd, param, data);
  }
}

void parseSerial(byte cmd, byte param, byte *data){
  Debug("parseSerial: packet received, cmd: ");
  Debug(cmd);
  Debug(", param: ");
  Debugln(param);
  switch (cmd)
  {
    case 0x00:
      test(param);
      break;
    case 0x0F:
      halt(param);
      break;
    case 0x10:
      setMotorMicroseconds(param, data);
      break;
    case 0x12:
      setMotorCalibrated(param, data);
      break;
    case 0x13:
      setMotorCalibration(param, data);
      break;
    case 0x30:
      getIMU(param);
      break;
    case 0x33:
      setAccelSettings(param, data);
      break;
    case 0x34:
      setGyroSettings(param, data);
      break;
    case 0x40:
      getVoltageAndTemperature(param);
      break;
    case 0x43:
      setVoltageCalibration(param, data);
      break;
    case 0x50:
      setAutoReport(param, data);
      break;
    case 0x51:
      setFeedback(param, data);
      break;
  }
}

void sendPacket(byte ogcmd, byte ogparam, byte cmd, byte param, byte *data){
  Debug("sendPacket: sending packet with cmd ");
  Debug(cmd);
  Debug(" and param ");
  Debugln(param);
  Comms.write(0xAC);            // header
  Comms.write(ogcmd);           // original cmd
  Comms.write(ogparam);         // original param
  Comms.write(cmd);             // cmd
  Comms.write(param);           // param
  for (int i = 0; i < 4; i++){  
    Comms.write(data[i]);       // data field
  }
  Comms.write(0x74);            // footer
}

void ok(byte ogcmd, byte ogparam){
  byte emptyDataField[4];
  if (enableFeedback){
    sendPacket(ogcmd, ogparam, 0x0A, 0xFF, emptyDataField);
  }
}

void fail(byte ogcmd, byte ogparam){
  byte emptyDataField[4];
  if (enableFeedback){
    sendPacket(ogcmd, ogparam, 0x0A, 0x00, emptyDataField);
  }
}

// test command: 0x00
void test(byte param){
  Debug("test: called with param ");
  Debugln(param);
  byte toSend[4];
  toSend[0] = VERSION;
  toSend[1] = 'p';
  toSend[2] = 'o';
  toSend[3] = 'g';
  // respond with 0x00 packet
  sendPacket(0x00, param, 0x00, 0xF0, toSend);
}

// halt command: 0x0F
void halt(byte param){
  Debugln("halt: HALTING!!!!!");
  setPWM(0, PWM_MID);
  setPWM(1, PWM_MID);
  setPWM(2, PWM_MID);
  setPWM(3, PWM_MID);
  setPWM(4, PWM_MID);
  ok(0x0F, param);
}

// setMotorMicroseconds command: 0x10
void setMotorMicroseconds(byte param, byte *data){
  Debug("setMotorMicroseconds: set motor ");
  Debug(param);
  Debug(" to ");
  uint16_t microseconds = data[0] * 0xFF + data[1];
  Debugln(microseconds);
  setPWM(param, microseconds);
  ok(0x10, param);
}

// setMotorCalibrated command: 0x12
void setMotorCalibrated(byte param, byte *data){
  Debug("setMotorCalibrated: set motor ");
  Debug(param);
  Debug(" to ");
  // data[0] should be int8_t... right?
  int8_t percent = data[0];
  Debugln(percent);
  setPercent(param, percent);
  ok(0x12, param);
}

// setMotorCalibration command: 0x13
void setMotorCalibration(byte param, byte *data){
  Debug("setMotorCalibrated: set motor ");
  Debug(param);
  Debug(" to ");
  uint16_t cal = data[0] * 0xFF + data[1];
  Debugln(cal);
  calibration[param] = cal;
  ok(0x13, param);
}

// getIMU command: 0x30
void getIMU(byte param){
  updateSensors();
  Debug("getIMU: getting ");
  switch (param)
  {
    case 0x15:
    {
      // accel
      Debugln("accelerometer data");
      byte *x = (byte *) &icmAccel.acceleration.x;
      byte *y = (byte *) &icmAccel.acceleration.y;
      byte *z = (byte *) &icmAccel.acceleration.z;
      sendPacket(0x30, 0x15, 0x3A, 0x00, x);
      sendPacket(0x30, 0x15, 0x3A, 0x30, y);
      sendPacket(0x30, 0x15, 0x3A, 0x60, z);
      break;
    }
    case 0x16:
    {
      // gyro
      Debugln("gyroscope data");
      byte *x = (byte *) &icmGyro.gyro.x;
      byte *y = (byte *) &icmGyro.gyro.y;
      byte *z = (byte *) &icmGyro.gyro.z;
      sendPacket(0x30, 0x15, 0x3C, 0x00, x);
      sendPacket(0x30, 0x15, 0x3C, 0x30, y);
      sendPacket(0x30, 0x15, 0x3C, 0x60, z);
      break;
    }
    default:
    {
      Debugln("getIMU: invalid IMU device");
      break;
    }
  }
}

// setAccelSettings command: 0x33
void setAccelSettings (byte param, byte *data){
  if (param != 0x15) { return; }
  Debugln("setAccelSettings: Accelerometer Settings Modified.");
  setAccelerometerRange(data[0]);
  setAccelerometerDivisor(data[1]);
  ok(0x33, param);
}

// setGyroSettings command: 0x34
void setGyroSettings (byte param, byte *data){
  if (param != 0x16) { return; }
  Debugln("setGyroSettings: Gyroscope Settings Modified.");
  setGyroscopeRange(data[0]);
  setGyroscopeDivisor(data[1]);
  ok(0x34, param);
}

// getVoltageAndTemperature command: 0x40
void getVoltageAndTemperature(byte param){
  if (param != 0x17) { return; }
  updateSensors();
  Debugln("getVoltageAndTemperature: getting voltage and temperature data");
  byte toSend[4];
  uint16_t temp = (uint16_t) (icmTemp.temperature * 100.0);
  uint16_t voltage = (uint16_t) (getVoltage(analogRead(VOLTAGE_PIN)) * 100.0);
  toSend[0] = temp % 0xFF;
  toSend[1] = temp / 0xFF;
  toSend[2] = voltage % 0xFF;
  toSend[3] = voltage / 0xFF;
  sendPacket(0x40, param, 0x44, 0x17, toSend);
}

// setVoltageCalibration command: 0x43
void setVoltageCalibration(byte param, byte *data){
  if (param != 0x17) { return; }
  Debug("setVoltageCalibration: new calibration = ");
  voltage_calibration = *(float *) &data;
  Debug(voltage_calibration);
  ok(0x43, param);
}

// setAutoReport command: 0x50
void setAutoReport(byte param, byte *data){
  if (param < 0x15 || param > 0x17) { return; }
  byte device = param - 0x15;
  enableAutoReport[device] = data[0] > 0;
  autoReportDelay[device] = data[1] * 0xFF + data[2];
  Debug("setAutoReport: AutoReport for device ");
  Debug(device);
  Debug(" is now ");
  Debugln(enableAutoReport[device]);
}

// setFeedback command: 0x51
void setFeedback(byte param, byte *data){
  Debug("setFeedback: feedback is now ");
  if (param != 0x01){
    fail(0x51, param);
  }
  enableFeedback = data[0] > 0x0;
  Debugln(enableFeedback);
}

// --------------- SECTION: PROGRAM LOOP --------------- //

void autoReport(){
  // iterate through devices
  for (int dev = 0; dev < 3; dev ++){
    if (enableAutoReport[dev]){
      if (millis() > autoReportTimers[dev]){
        if (millis() - autoReportTimers[dev] > 2 * autoReportDelay[dev]){
          Debug("autoReport: OVERLOAD!!! Device ");
          Debug(dev);
          Debug(" is running ");
          Debug(millis() - autoReportTimers[dev]);
          Debugln("ms behind.");
        }
        autoReportTimers[dev] = millis() + autoReportDelay[dev];
        switch (dev)
        {
          case 0: // accelerometer
            getIMU(0x15);
            break;
          case 1: // gyroscope
            getIMU(0x16);
            break;
          case 2: // volt/temp
            getVoltageAndTemperature(0x17);
            break;
          default:
            Debugln("autoReport: What? This shouldn't be possible!");
            break;
        }
      } // end if timer active
    } // end if enabled
  } // end for
}

void loop() {
  readSerial();
  autoReport();
}
