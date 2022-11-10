#include "stepper.h"
#include "bsp.h"

void setup() {
  stepper_setup();
  Serial.begin(9600);
}

MOVE moves[] = {
  {1000, 100000, 2000},
  {300, 200000, 1000},
  {2000, 500000, 5000},
  {0, 800000, 1500},
};
int num_moves = 4;
int move_index = 0;
bool test = true;

void loop() {
  stepper_tasks();
  if (stepper_move_complete() and test) {
    Serial.print("testing ");
    Serial.print(move_index);
    Serial.print("...\n");
    stepper_move(moves[move_index]);
    if (++move_index == num_moves) {
      move_index = 0;
      // test = false;
    }
  }
}
