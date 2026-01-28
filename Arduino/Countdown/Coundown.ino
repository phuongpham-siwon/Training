/*
  Countdown from a number and EXPLODE! 
  with one second inbetween.
    A
   ---
F |   | B
  | G |
   ---
E |   | C
  |   |
   ---
    D
  This example code is in the public domain.
 */
 
// Pin 2-8 is connected  to the 7 segments of the display.
// Display is Common Anode (Light on when LOW)
#define SEG_ON  HIGH
#define SEG_OFF LOW

#define DIGIT_ON  LOW
#define DIGIT_OFF HIGH

int pinA = 2;
int pinB = 3;
int pinC = 4;
int pinD = 5;
int pinE = 6;
int pinF = 7;
int pinG = 8;
int D1 = 9;
int D2 = 10;
int D3 = 11;
int D4 = 12;
int DP = 13;

int thousand = D1;
int hundred  = D2;
int ten      = D3;
int one      = D4;

const int digitPins[4] = {thousand, hundred, ten, one};
const int segmentPins[7] = {pinA, pinB, pinC, pinD, pinE, pinF, pinG}; 
const uint8_t digitMap[10] = {
  // GFEDCBA, 1 is on, 0 is off
  0b00111111, // 0
  0b00000110, // 1
  0b01011011, // 2
  0b01001111, // 3
  0b01100110, // 4
  0b01101101, // 5
  0b01111101, // 6
  0b00000111, // 7
  0b01111111, // 8
  0b01101111  // 9
};

// the setup routine  runs once when you press reset:
void setup() {                
  // initialize  the digital pins as outputs.
  pinMode(pinA, OUTPUT);     
  pinMode(pinB,  OUTPUT);     
  pinMode(pinC, OUTPUT);     
  pinMode(pinD, OUTPUT);     
  pinMode(pinE, OUTPUT);     
  pinMode(pinF, OUTPUT);     
  pinMode(pinG,  OUTPUT);   
  pinMode(D1, OUTPUT);  
  pinMode(D2, OUTPUT);  
  pinMode(D3,  OUTPUT);  
  pinMode(D4, OUTPUT);  
}

// on display:    D1  D2  D3  D4 
// number 1234:   1   2   3   4
// position:  thousand 
//                 hundred
//                       ten
//                           one
void split_number(int number, int digits[4]){
  // digits = {thousand, hundred, ten, one}
  digits[0] = (number / 1000) % 10;  // thousand
  digits[1] = (number / 100) % 10;   // hundred
  digits[2] = (number / 10) % 10;    // ten
  digits[3] = number %  10;          // one
}

void digit_on(int number, double index){
  digitalWrite(digitPins[0], (index == 0 && number >= 1000) ? DIGIT_ON : DIGIT_OFF);
  digitalWrite(digitPins[1], (index == 1 && number >= 100) ? DIGIT_ON : DIGIT_OFF);
  digitalWrite(digitPins[2], (index == 2 && number >= 10)  ? DIGIT_ON : DIGIT_OFF);
  digitalWrite(digitPins[3], index == 3 ? DIGIT_ON : DIGIT_OFF);
}

void display_segment(int number) {
  uint8_t mask = digitMap[number];

  for (int i = 0; i < 7; i++) { // iterate thru each bit
    bool segmentOn = mask & (1 << i);
    digitalWrite(segmentPins[i], segmentOn ? SEG_ON : SEG_OFF);
  }
}

void all_digits_off() {
  for (int i = 0; i < 4; i++) {
    digitalWrite(digitPins[i], DIGIT_OFF);
  }
}

void all_segment_off(){
  for (int i = 0; i < 7; i++) {
    digitalWrite(segmentPins[i], SEG_OFF);
  } 
}

void display(int number) {
  int digits[4];
  split_number(number, digits);

  for (int i = 0; i < 4; i++){
    all_digits_off();
    display_segment(digits[i]); // Segments should change when no digit is active
    digit_on(number, i);        // Then digit pin on => this avoid ghosting (dim residual light on)
    
    delayMicroseconds(1000);
  }
}

unsigned long lastStep = 0;
void chaos(){
  int chaosPins[6] = {pinA, pinF, pinE, pinD, pinC, pinB};
  int i = 0;
  while (i < 6){
    if (millis() - lastStep >= 200) {
      lastStep = millis();
      all_digits_off();
      all_segment_off();
      digitalWrite(chaosPins[i], SEG_ON);
      digitalWrite(digitPins[0], DIGIT_ON);
      digitalWrite(digitPins[1], DIGIT_ON);
      digitalWrite(digitPins[2], DIGIT_ON);
      digitalWrite(digitPins[3], DIGIT_ON);
      i++;
    }
  } 
}

unsigned long lastTick = 0;
int number = 3;
void loop() {
  if (number > 0) {
    display(number);
  } else{
    chaos();
  }
  
  if (millis() - lastTick >= 1000){
    lastTick = millis();
    number --;
  }
  
}