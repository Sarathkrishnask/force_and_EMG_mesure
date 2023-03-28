/*
  AnalogReadSerial

  Reads an analog input on pin 0, prints the result to the Serial Monitor.
  Graphical representation is available using Serial Plotter (Tools > Serial Plotter menu).
  Attach the center pin of a potentiometer to pin A0, and the outside pins to +5V and ground.

  This example code is in the public domain.

  https://www.arduino.cc/en/Tutorial/BuiltInExamples/AnalogReadSerial
*/

#include "HX711.h"
#include <Encoder.h>

// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 3;
const int LOADCELL_SCK_PIN = 4;
const byte interruptPin =2;
long reading,offset=0;
float weight=0;
//uint16_t enc_=0;
//bool state = HIGH;
int ledPin = 10;
volatile byte state = LOW;
signed int emg1_ =A1;
signed int emg2_ =A2;
Encoder myEnc(5, 6);

HX711 scale;

typedef union {
  float val_;
  unsigned long value;
  byte bytes[4];
} LongBytes;


long oldPosition  = -999;
LongBytes force, emg_chnl_1,emg_chnl_2, encoder_,timeVal;

// the setup routine runs once when you press reset:
void setup() {
  // initialize Serial communication at 9600 bits per second:
  Serial.begin(115200);
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  pinMode(interruptPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(interruptPin), blink, CHANGE);
  pinMode(ledPin,OUTPUT);
}

void blink(){
  offset = scale.read_average();
}
void count(){

  state = !state;

} 

// the loop routine runs over and over again forever:
void loop() {
  count();
  digitalWrite(ledPin, state);
//  Serial.println(state);

  byte header[] = {0xFF, 0xFF, 0x00};
  byte chkSum = 0xFE;
  byte _temp;
  long newPosition = myEnc.read();
  if (newPosition != oldPosition) {
    oldPosition = newPosition;
  }
  encoder_.value = newPosition;
  load_cell();
  emg_chnl_1.val_ = analogRead(emg1_);
  emg_chnl_2.val_ = analogRead(emg1_);
  timeVal.value = millis();
  // Send header

  header[2] = 20 + 1;
  chkSum += header[2];

  Serial.write(header[0]);
  Serial.write(header[1]);
  Serial.write(header[2]);


  // print out the value you read:
  //  Serial.write(sensorValue);
  

  for (int i = 0; i < 4; i++) {
    Serial.write(force.bytes[i]);
    chkSum += force.bytes[i];
  }
  for (int i = 0; i < 4; i++) {
    Serial.write(emg_chnl_1.bytes[i]);
    chkSum += emg_chnl_1.bytes[i];
  }
  for (int i = 0; i < 4; i++) {
    Serial.write(emg_chnl_2.bytes[i]);
    chkSum += emg_chnl_2.bytes[i];
  }
    for (int i = 0; i < 4; i++) {
  Serial.write(encoder_.bytes[i]);
  chkSum += encoder_.bytes[i];
  }
    
  for (int i = 0; i < 4; i++) {
    Serial.write(timeVal.bytes[i]);
    chkSum += timeVal.bytes[i];
  }
  Serial.write(chkSum);
    delayMicroseconds(960);     // delay in between reads for stability

}

void load_cell(){
  if(scale.is_ready()){
  reading = (scale.get_units() - offset);
  weight = (reading / 44.473);
//  Serial.println(weight / 1000);

  force.val_ = (weight / 1000);
  }
  else{
    force.val_=(weight / 1000);
  }
  
}
