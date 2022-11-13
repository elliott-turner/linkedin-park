#include "stepper.h"

int current_position = 0;
int move_distance = 0;
int move_direction = 1;
int move_position = 0;
int move_accel_distance = 0;
bool move_has_coast = true;
long long int move_velocity = 0;
int move_acceleration = 0;

enum state {
  homing_1,
  homing_2,
  homing_3,
  starting,
  calculating,
  step_high,
  step_low,
  waiting
};
enum state current_state = homing_1;

unsigned long last_time = 0;
float T = 0;

void stepper_setup() {
  pinMode(EN_PIN, OUTPUT);
  pinMode(MS1_PIN, OUTPUT);
  pinMode(MS2_PIN, OUTPUT);
  pinMode(MS3_PIN, OUTPUT);
  pinMode(RST_PIN, OUTPUT);
  pinMode(SLP_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(END_PIN, INPUT_PULLDOWN_16);

  // full step
  digitalWrite(MS1_PIN, LOW);
  digitalWrite(MS2_PIN, LOW);
  digitalWrite(MS3_PIN, LOW);

  // enable
  digitalWrite(EN_PIN, LOW);

  // no sleep
  digitalWrite(SLP_PIN, HIGH);

  // no reset
  digitalWrite(RST_PIN, HIGH);
}

void stepper_tasks() {
  unsigned long current_time = micros();
  long long int velocity = 0;
  float T_0, T_1;
  switch (current_state) {
    case (homing_1):
      digitalWrite(DIR_PIN, LOW);
      if (current_time - last_time >= 1000) {
        digitalWrite(STEP_PIN, LOW);
        last_time = current_time;
      }
      if (current_time - last_time >= 500) {
        digitalWrite(STEP_PIN, HIGH);
      }
      if (digitalRead(END_PIN)) {
        digitalWrite(STEP_PIN, LOW);
        current_state = homing_2;
      }
      break;

    case (homing_2):
      digitalWrite(DIR_PIN, HIGH);
      if (current_time - last_time >= 2000) {
        digitalWrite(STEP_PIN, LOW);
        last_time = current_time;
        current_position++;
      }
      if (current_time - last_time >= 1000) {
        digitalWrite(STEP_PIN, HIGH);
      }
      if (current_position >= 100) {
        digitalWrite(STEP_PIN, LOW);
        current_state = homing_3;
      }
      break;

    case (homing_3):
      digitalWrite(DIR_PIN, LOW);
      if (current_time - last_time >= 2000) {
        digitalWrite(STEP_PIN, LOW);
        last_time = current_time;
      }
      if (current_time - last_time >= 1000) {
        digitalWrite(STEP_PIN, HIGH);
      }
      if (digitalRead(END_PIN)) {
        digitalWrite(STEP_PIN, LOW);
        current_position = 0;
        current_state = waiting;
      }
      break;

    case (starting):
      digitalWrite(DIR_PIN, move_direction > 0); // set move direction
      move_position = 0; // reset move odometer
      last_time = current_time; // set start time of first pulse
      // calculate acceleration distance and determine if trajectory is triangular or trapezoidal
      move_accel_distance = move_velocity*move_velocity/2/move_acceleration;
      if (move_accel_distance >= move_distance / 2) {
        move_accel_distance = move_distance / 2;
        move_has_coast = false;
      }
      else {
        move_has_coast = true;
      }
      current_state = calculating;
      break;

    case (calculating):
      // coast
      T_0 = (float)move_position/(float)move_velocity;
      T_1 = (float)(move_position+1)/(float)move_velocity;
      if (move_position < move_accel_distance) { // accelerate
        T_0 = sqrt(2.0*(float)move_acceleration*(float)move_position)/((float)move_acceleration);
        T_1 = sqrt(2.0*(float)move_acceleration*(float)(move_position+1))/((float)move_acceleration);
      }
      if (move_position > move_distance-move_accel_distance) { // decelerate
        T_0 = -1.0*sqrt(2.0*(float)move_acceleration*((float)move_distance-(float)move_position))/((float)move_acceleration);
        T_1 = -1.0*sqrt(2.0*(float)move_acceleration*((float)move_distance-(float)(move_position+1)))/((float)move_acceleration);
      }
      T = (T_1-T_0)*1000000.0; // step period [us]
      current_state = step_high;
      break;

    case (step_high):
      if (current_time - last_time > (int)(T / 2.0)) {
        digitalWrite(STEP_PIN, HIGH);
        delayMicroseconds(10);
        current_state = step_low;
      }
      break;

    case (step_low):
      if (current_time - last_time > (int)T) {
        digitalWrite(STEP_PIN, LOW);
        last_time = current_time;
        move_position++;
        if (move_position >= move_distance) {
          current_state = waiting;
          current_position += move_position*move_direction;
        }
        else {
          current_state = calculating;
        }
      }
      break;
  }
}

void stepper_move(MOVE move) {
  move_distance = move.position - current_position;
  if (move_distance < 0) {
    move_direction = -1;
    move_distance *= -1;
  }
  else {
    move_direction = 1;
  }
  move_acceleration = move.acceleration;
  move_velocity = move.velocity;
  current_state = starting;
}

bool stepper_move_complete() {
  return (current_state == waiting);
}
