// pwm test
// uses human readable space separated instructions
// for example, "/3 1800" (cmd, pins[3] to 1800)

#include <Servo.h>

#define MID 1500
#define MIN 1000
#define MAX 2000

int pins[] = {A4, A5, 9, 10, 11};
Servo servos[5];

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 5; i++){
    servos[i].attach(pins[i]); 
  }
}

void loop() {
  if (Serial.available()){
    // read until "/"
    Serial.readStringUntil('/');
    char i = Serial.read() - 48; // convert to number
    char space = Serial.read();
    char a = Serial.read() - 48;
    char b = Serial.read() - 48;
    char c = Serial.read() - 48;
    char d = Serial.read() - 48;
    int val = a * 1000 + b * 100 + c * 10 + d;
    servos[i].writeMicroseconds(val);
    Serial.print("Set pin ");
    Serial.print((int) i);
    Serial.print(" at ");
    Serial.print(pins[i]);
    Serial.print(" to ");
    Serial.println(val);
  }
}
