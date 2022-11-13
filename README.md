# LinkedIn Park
Project for ME366J at the University of Texas at Austin

## Theory of Operation

### Communication Protocol
To control the instrument, the GUI sends commands over serial that are then processed. The format and functionality of these commands are described below.

#### Move Command
The move command moves the roller to the specified position (absolute) following a trapezoidal trajectory with specified maximum velocity and acceleration.

`M <position> <max_velocity> <max_acceleration>\n`

| variable | description |
| - | - |
| `position` | absolute position to move to [steps] |
| `max_velocity` | maximum velocity [steps/s] |
| `max_acceleration` | maximum acceleration [steps/s/s] |
