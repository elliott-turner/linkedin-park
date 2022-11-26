#ifndef STEPPER_H
#define STEPPER_H

#include <Arduino.h>
#include "bsp.h"

typedef struct MOVE {
  unsigned int position;
  unsigned int acceleration;
  unsigned int velocity;
} MOVE;

void stepper_setup();
void stepper_tasks();
void stepper_move(MOVE move);
bool stepper_move_complete();

#endif
