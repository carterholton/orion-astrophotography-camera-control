# Orion Smart Camera Control System
Orion is a Raspberry-Pi-based DSLR control system designed to streamline the astrophotography process. It combines a software-based intervalometer, a camera focus assistant, project management features, and automatic pre-processing workflows into one piece of hardware.

## How It Works
The foundation of this project is the gphoto2 software, which allows users to interact with supported cameras via the command line on a connected computer. Orion leverages this core functionality to build advanced features specifically tailored to astrophotography, while also incorporating a custom UI to maximize efficiency and usability. 

My current setup utilizes a Raspberry Pi enclosed in a 3D-printed case with a 20x04 LCD display. Connected via serial, An Arduino-powered joystick is used for user input. The user is guided through each step in the shooting process. 

### Features
Current features include:
- setting exposure length, interval between shots, and ISO
- setting focus using the connected joystick, allowing for very precise adjustments
- taking test shots to check framing and light levels
- functioning as an intervalometer, with shooting progress shown on LCD
- one-click dark frame capture at the conclusion of shooting
- more features on the way!

## Project Management
Project management is a core focus of this project. Orion allows for the storage of up to 4 projects simulaneously. A "project" refers to shooting sessions related to a specific target. Each project can have custom pre-defined camera settings, as well as a "goal" total exposure time for that target. For example, say over the course of 3 days I photograph the Orion Nebula, the Andromeda Galaxy, and the Pleiades star cluster, with multiple shooting sessions for each. At the beginning of each session, I can choose my current target from the on-screen menu and Orion will automatically display the total combined exposure time for that project, as well as the percent completion of the "goal" exposure time. 
