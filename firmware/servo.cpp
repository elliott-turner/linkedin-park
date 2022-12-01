#include "servo.h"

enum servo_position {
    left,
    right,
};
enum servo_position servo_position = left;

enum state {
  ready,
  plucking,
};
enum state current_state = plucking;

Servo ser;

void servo_setup() {
  pinMode(SERVO_PIN, OUTPUT);
  ser.attach(SERVO_PIN);
  ser.write(POS_LEFT);
}

unsigned long pluck_start_time;

void servo_tasks() {
  unsigned long current_time = micros();
  switch (current_state) {
    case (plucking):
      if (current_time - pluck_start_time >= PLUCK_TIME) {
        switch (servo_position) {
          case(left):
            ser.write(POS_LEFT_STBY);
            break;
          case (right):
            ser.write(POS_RIGHT_STBY);
        }
        current_state = ready;
      }
  }
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
  current_state = plucking;
  pluck_start_time = micros();
}
