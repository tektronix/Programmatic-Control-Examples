# Combining 2 PSU Channels in Series

Combines channel sourcing in series to increase voltage capabilities.

## Required Modules
1 x MPSU50-2ST

## Available Languages
* TSP

## Instructions
1. Begin by connecting to the mainframe using the instrument panel found on the left side of the visual studio code interface or running the TSP: Connect function and entering the IP address.
2. Connect CH1-LO to CH2-HI. Then connect the load to CH1-HI and CH2-LO
3.	Configure the slot number, voltage source level, and current limit as desired, located at the top of the script.
* NOTE: Each channel is set with a voltage level that is half the input voltage level and both channels are set with the current limit specified. These parameters must fall in the power envelope per channel of the module.
4.	Run Series_Combo.tsp and view the current/voltage readings from both channels.
