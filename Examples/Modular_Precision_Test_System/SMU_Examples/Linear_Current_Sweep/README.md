# Linear Current Sweep

Configures and executes a linear current sweep while measuring voltage.

NOTE: There are two functions provided that are nearly identical except for how they manage timing. “DC_Current_Sweep_Diode_RunTimeEnv” uses the delay() function for timing while “DC_Current_Sweep_Diode_inTriggerModel” uses the trigger model. The trigger model is used by default as the timing is more accurate. To change this simply change which function call is commented at the bottom of the script.

## Required Modules
1 x MSMU60-2

## Available Languages
* TSP
* Python

## Instructions
1. Adjust parameters and run code