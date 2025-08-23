# Orion Smart Camera Control System
Orion is a Raspberry-Pi-based DSLR control system designed to streamline the astrophotography process. It combines a software-based intervalometer, a camera focus assistant, project management features, and automatic pre-processing workflows into one piece of hardware.

## How It Works
The foundation of this project is the gphoto2 software, which allows users to interact with supported cameras via the command line on a connected computer. Orion leverages this core functionality to build advanced features specifically tailored to astrophotography.

My current setup utilizes a Raspberry Pi enclosed in a 3D-printed case with a 20x04 LCD display. Connected via serial, An Arduino-powered joystick is used for user input. The user is guided through each step in the shooting process. Current features include:
- setting exposure length, interval between shots, and ISO
- setting focus using the connected joystick, allowing for very precise adjustments
- taking test shots to check framing and light levels
- functioning as an intervalometer, with shooting progress shown on LCD
- one-click dark frame capture at the conclusion of shooting
