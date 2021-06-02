// multi-serial test
// feeds SerialA into SerialB and vice versa.

// for ATSAMD21/D51: Serial, Serial1
// for STM32duino: SerialUSB, Serial
#define SerialA Serial
#define SerialB Serial1

// test using any baudrate you like
#define BAUDRATE 230400

void setup() {
  SerialA.begin(BAUDRATE);
  SerialB.begin(BAUDRATE);
}

void loop() {
  if (SerialA.available()){
    SerialB.write(SerialA.read());
  }
  if (SerialB.available()){
    SerialA.write(SerialB.read());
  }
}
