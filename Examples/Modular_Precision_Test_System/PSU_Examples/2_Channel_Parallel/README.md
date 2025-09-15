# Combining 2 PSU Channels in Parallel

Combines channel sourcing in parallel to increase current capabilities. 

## Required Modules
1 x MPSU50-2ST

## Available Languages
* TSP

## Instructions
1. Begin by connecting to the mainframe using the instrument panel found on the left side of the visual studio code interface or running the TSP: Connect function and entering the IP address.
2. Connect CH1-LO to CH2-LO and CH1-HI to CH2-HI. Then connect the load to CH1.
3.	Configure the slot number, voltage source level, current level, and current limit as desired, located at the top of the script.
* NOTE: To avoid one of the PSU’s sinking the other the source settings must be set carefully. One channel has a voltage level that is slightly higher than the target voltage and the other has a current slightly higher than target current. The source levels for both channels must fall under the power envelope for the module. 
4.	Run Parallel _Combo.tsp and view the current/voltage readings from both channels.
