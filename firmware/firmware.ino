#include "stepper.h"
#include "servo.h"
#include "serial_cmd.h"

void setup() {
  stepper_setup();
  servo_setup();
  serial_cmd_setup();
}

void loop() {
  stepper_tasks();
  servo_tasks();
  serial_cmd_tasks();
}
