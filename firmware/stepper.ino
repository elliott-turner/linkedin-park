#include "stepper.h"

int current_position = 0;
int move_distance = 0;
int move_direction = 1;
int move_position = 0;
int move_accel_distance = 0;
long long int move_velocity = 0;
long long int current_velocity = 0;
long long int move_max_velocity = 0;
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
unsigned long accel_time = 0;
unsigned long decel_time = 0;
int step_time = 0;

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
      if (move_direction > 0) { digitalWrite(DIR_PIN, HIGH); }
      else { digitalWrite(DIR_PIN, LOW); }
      last_time = current_time;
      accel_time = last_time;
      current_state = calculating;
      Serial.print(move_distance);
      Serial.print(" ");
      Serial.print(move_accel_distance);
      Serial.print("\n");
      break;
    case (calculating):
      if (move_position <= move_accel_distance) {
        current_velocity = (current_time - accel_time) * move_acceleration / 1000000;
        if (current_velocity > move_velocity) { current_velocity = move_velocity; }
      }
      if (move_position == move_distance - move_accel_distance) {
        move_max_velocity = current_velocity;
        decel_time == current_time;
      }
      if (move_position >= move_distance - move_accel_distance) {
        current_velocity = move_max_velocity - (current_time - decel_time) * move_acceleration / 1000000;
        if (current_velocity < 0) { current_velocity = 0; }
      }
      velocity = current_velocity;
      if (velocity < 100) { velocity = 100; }
      step_time = 1000000 / velocity;
      current_state = step_high;
      break;
    case (step_high):
      if (current_time - last_time > step_time / 2) {
        digitalWrite(STEP_PIN, HIGH);
        delayMicroseconds(10);
        current_state = step_low;
      }
      break;
    case (step_low):
      if (current_time - last_time > step_time) {
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
  move_position = 0;
  move_acceleration = move.acceleration;
  move_velocity = move.velocity;
  move_accel_distance = (move_velocity * move_velocity) / 2 / move_acceleration;
  if (move_accel_distance > move_distance / 2) { move_accel_distance = move_distance / 2; }
  current_state = starting;
}

bool stepper_move_complete() {
  return (current_state == waiting);
}
