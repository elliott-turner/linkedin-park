#include "servo.h"

enum servo_position {
    left,
    right,
};
enum servo_position servo_position = left;

Servo ser;

void servo_setup() {
  pinMode(SERVO_PIN, OUTPUT);
  ser.attach(SERVO_PIN);
  ser.write(POS_LEFT);
}

void servo_pluck() {
  switch (servo_position) {
    case(left):
      ser.write(POS_RIGHT);
      servo_position = right;
      break;
    case(right):
      ser.write(POS_LEFT);
      servo_position = left;
      break;
  }
}
