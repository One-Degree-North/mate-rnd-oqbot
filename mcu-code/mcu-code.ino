/* microcontroller-side code for MATE R&D OQBot
** refer to docs/packet-structure and docs/command-list for more details
** status:
** implemented: 0x00, 0x0F
** not implemented: 0x10, 0x12, 0x13, 0x30, 0x33, 0x34, 0x40, 0x43, 0x50, 0x51
 */


// --------------- SECTION: DEFINITIONS --------------- //

#include <Adafruit_ICM20649.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <Servo.h>

#define VERSION 0

// define our two Serial connections
#define Debug Serial
#define Comms Serial1
#define DEBUG_BAUDRATE 230400
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

// values for settings
byte enableFeedback = 0xFF;
byte enableAutoReport = 0x00;

// --------------- SECTION: INITIALIZATION --------------- //

void initSerial() {
  Debug.begin(DEBUG_BAUDRATE);
  Comms.begin(COMMS_BAUDRATE);
  delay(200);
  Debug.println("initSerial: Serial Init complete");
}

void setDefaultRanges(){
  icm.setAccelRange(ICM20649_ACCEL_RANGE_16_G);
  icm.setGyroRange(ICM20649_GYRO_RANGE_500_DPS);
  icm.setAccelRateDivisor(15); 
  icm.setGyroRateDivisor(15);
  Debug.println("setDefaultRanges: ICM20649 default ranges set.");
}

void initSensors() {
  if (!icm.begin_I2C()){
    Debug.println("initSensors: ICM20649 Init over I2C failed.");
    while(true){
      delay(10);
    }
  }
  Debug.println("initSensors: ICM20649 Init complete");
  setDefaultRanges();
}

void initMotors() {
  for (int i = 0; i < NUM_MOTORS; i++){
    motors[i].attach(pins[i]); 
    Debug.print("initMotors: motor ");
    Debug.print(i);
    Debug.print(" attached to pin ");
    Debug.println(pins[i]);
  }
  Debug.println("initMotors: Motor Init complete");
}

void setup() {
  initSerial();
  initSensors();
  initMotors();
}

// --------------- SECTION: HELPER FUNCTIONS --------------- //

float getVoltage(int rawInput){
  return (rawInput / 1024.0) * (R1 + R2) / R2 * voltage_calibration;
}

// --------------- SECTION: SERIAL COMMUNICATION --------------- //

void readSerial(){
  if (Comms.available() >= 8){
    // read Comms until header is received or not enough bytes
    byte header = 0x00;
    while (Comms.available() >= 7 && header != 0xCA){
      header = Comms.read();
    } 
    // verify header
    if (header != 0xCA) {
      Debug.println("readSerial: packet received, but header did not match.");
      return; 
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
      Debug.println("readSerial: packet received, but footer did not match.");
      return;
    }
    // call parseSerial
    parseSerial(cmd, param, data);
  }
}

void parseSerial(byte cmd, byte param, byte *data){
  Debug.print("parseSerial: packet received, cmd: ");
  Debug.println(cmd);
  switch (cmd)
  {
    case 0x00:
      test(param);
      break;
    case 0x0F:
      halt(param);
      break;
    case 0x10:
      // setMotorMicroseconds(param, data);
      break;
    case 0x12:
      // setMotorCalibrated(param, data);
      break;
    case 0x13:
      // setMotorCalibration(param, data);
      break;
    case 0x30:
      // getIMU(param);
      break;
    case 0x33:
      // setAccelSettings(param, data);
      break;
    case 0x34:
      // setGyroSettings(param, data);
      break;
    case 0x40:
      // getVoltageAndTemperature(param);
      break;
    case 0x43:
      // setVoltageCalibration(param, data);
      break;
    case 0x50:
      // setAutoReport(param, data);
      break;
    case 0x51:
      // setFeedback(param, data);
      break;
  }
}

void sendPacket(byte ogcmd, byte ogparam, byte cmd, byte param, byte *data){
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

// test command: 0x00
void test(byte param){
  Debug.print("test: called with param ");
  Debug.println(param);
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
  Debug.println("halt: HALTING!!!!!");
  ok(0x0F, param);
}

// --------------- SECTION: PROGRAM LOOP --------------- //

void loop() {
  readSerial();
}
