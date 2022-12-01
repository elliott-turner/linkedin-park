#ifndef SERVO_H
#define SERVO_H

#include <Arduino.h>
#include <Servo.h>
#include "bsp.h"

#define POS_LEFT 50
#define POS_LEFT_STBY 80
#define POS_RIGHT 125
#define POS_RIGHT_STBY 95

#define PLUCK_TIME 80000

void servo_setup();
void servo_tasks();
void servo_pluck();

#endif
