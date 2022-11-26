#ifndef SERIAL_CMD_H
#define SERIAL_CMD_H

#include <Arduino.h>
#include "stepper.h"

#define CMD_STR_SIZE 64

void serial_cmd_setup();
void serial_cmd_tasks();

#endif
