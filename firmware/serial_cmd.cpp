#include "serial_cmd.h"

enum serial_cmd_state {
  waiting,
  processing,
  executing,
};
enum serial_cmd_state current_serial_cmd_state = waiting;

char command_string[CMD_STR_SIZE] = {0x0};
unsigned int command_string_index = 0;

void serial_cmd_setup() {
    Serial.begin(115200);
}

void serial_cmd_tasks() {
  switch (current_serial_cmd_state) {
    case (waiting):
      if (Serial.available() > 0) {
        char c = Serial.read();
        delay(3);
        if (c == '\n') {
          current_serial_cmd_state = processing;
          break;
        }
        command_string[command_string_index++] = c;
        break;
      }
    
    case (processing):
      switch (command_string[0]) {
        case ('M'): // move command
          MOVE move;
          sscanf(command_string, "M %u %u %u", &move.position, &move.velocity, &move.acceleration);
          Serial.print("\n");
          Serial.print(move.position);
          Serial.print("\n");
          Serial.print(move.velocity);
          Serial.print("\n");
          Serial.print(move.acceleration);
          Serial.print("\n");
          stepper_move(move);
          break;
      }
      memset(command_string, 0x0, CMD_STR_SIZE);
      command_string_index = 0;
      current_serial_cmd_state = executing;
      break;
    
    case (executing):
      if (stepper_move_complete()) { current_serial_cmd_state = waiting; }
  }
}
