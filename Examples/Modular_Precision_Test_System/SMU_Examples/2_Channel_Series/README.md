# Combining 2 SMU Channels in Series

Combines channel sourcing in series to increase voltage capabilities.

By default, the scripts sweep each channel from 0-10V. However, the total voltage reads from 0-20V.


## Required Modules
1 x MSMU60-2

## Available Languages
* TSP
* Python

## Instructions
1. Begin by connecting to the mainframe using the instrument panel found on the left side of the visual studio code interface or running the TSP: Connect function and entering the IP address.
2. Connect CH1 LO to CH2 LO and CH1 HI to CH2 HI.
3. Connect leads from CH2 HI/LO to the 10 kΩ.
4. Run Code
