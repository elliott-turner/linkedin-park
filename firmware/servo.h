#ifndef SERVO_H
#define SERVO_H

#include <Arduino.h>
#include <Servo.h>
#include "bsp.h"

#define POS_LEFT 60
#define POS_RIGHT 120

void servo_setup();
void servo_pluck();

#endif
