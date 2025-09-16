# Pulsed Linear Current Sweep

Configures and executes a pulsed current sweep while measuring at the peaks of the pulse.

NOTE: There are two functions provided that are nearly identical except for how they manage timing. “Pulse_Current_Sweep_Diode_inDelayConstant” uses a delay constant for timing while “Pulse_Current_Sweep_Diode_inTriggerTimer” uses the trigger model. The trigger model is used by default. To change this simply change which function call is commented at the bottom of the script. 

## Required Modules
1 x MSMU60-2

## Available Languages
* TSP
* Python

## Instructions
1. Adjust parameters and run code