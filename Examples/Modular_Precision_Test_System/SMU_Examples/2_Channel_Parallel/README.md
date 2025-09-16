# Combining 2 SMU Channels in Parallel

Combines channel sourcing in parallel to increase current capabilities.

By default, the scripts set each channel to a current limit of 100 mA however the output is measured at nearly 200 mA. The output current has been combined in parallel to extend the current capabilities of each channel.

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
