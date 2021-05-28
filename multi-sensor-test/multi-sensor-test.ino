// multi sensor test
// sensors used: ICM20649 imu + 2.39MOhm voltage calibrator

#include <Adafruit_ICM20649.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

// voltage calibrator
#define VOLTAGE_PIN A2
#define R1 2000000
#define R2 390000

// ICM20649
#define INTERVAL_MS 100
Adafruit_ICM20649 icm;

void setup() {
  Serial.begin(115200);
  while(!Serial) {delay(10);}
  Serial.println("IMU + Voltmeter test for MATE R&D OQBot");
  if (!icm.begin_I2C()){
    Serial.println("icm init failed");
    while(true){
      delay(10);
    }
  }
  Serial.println("IMU20649 connected over I2C");
  setRanges();
  delay(1000);
}

void loop() {
  sensors_event_t accel;
  sensors_event_t gyro;
  sensors_event_t temp;
  icm.getEvent(&accel, &gyro, &temp);
  double voltage = getVoltage(analogRead(VOLTAGE_PIN));

  Serial.print("temp: ");
  Serial.print(temp.temperature);
  Serial.println("C");

  Serial.print("accel x: ");
  Serial.print(accel.acceleration.x);
  Serial.print(", y: ");
  Serial.print(accel.acceleration.y);
  Serial.print(", z: ");
  Serial.print(accel.acceleration.z);
  Serial.println(" (m/s^2) ");

  Serial.print("gyro x: ");
  Serial.print(gyro.gyro.x);
  Serial.print(", y: ");
  Serial.print(gyro.gyro.y);
  Serial.print(", z: ");
  Serial.print(gyro.gyro.z);           
  Serial.println(" (radians/s) ");

  Serial.print("voltage: ");
  Serial.println(voltage);

  Serial.println("------------------");

  delay(INTERVAL_MS);
}

void setRanges(){
  icm.setAccelRange(ICM20649_ACCEL_RANGE_16_G);
  icm.setGyroRange(ICM20649_GYRO_RANGE_500_DPS);
  icm.setAccelRateDivisor(10); 
  icm.setGyroRateDivisor(10);
  
  uint16_t accel_divisor = icm.getAccelRateDivisor();
  float accel_rate = 1125 / (1.0 + accel_divisor);

  Serial.print("Accelerometer data rate divisor set to: ");
  Serial.println(accel_divisor);
  Serial.print("Accelerometer data rate (Hz) is approximately: ");
  Serial.println(accel_rate);

  uint8_t gyro_divisor = icm.getGyroRateDivisor();
  float gyro_rate = 1100 / (1.0 + gyro_divisor);

  Serial.print("Gyro data rate divisor set to: ");
  Serial.println(gyro_divisor);
  Serial.print("Gyro data rate (Hz) is approximately: ");
  Serial.println(gyro_rate);
  Serial.println();
}

double getVoltage(int rawInput){
  double recorded_voltage = rawInput / 1024.0;
  // 7.55 is my magic number that I calibrated using four known power sources
  return recorded_voltage * (R1+R2) / R2 * 7.55;
}
