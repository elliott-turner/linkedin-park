#include "stepper.h"
#include "serial_cmd.h"
#include "bsp.h"

void setup() {
  stepper_setup();
  serial_cmd_setup();
}

void loop() {
  stepper_tasks();
  serial_cmd_tasks();
}
