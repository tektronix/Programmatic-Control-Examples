# DC/Pulse LIV Characterization for VCSEL

Two channels are used to perform a voltage and current sweep for an LIV characterization of a VCSEL. Measurements are recorded throughout the test.

NOTE: There are three functions provided, “DC_Laser_VCSEL_LIV_RunTimeEnv” is the simplest however as it does not utilize a trigger model timings are less accurate. “DC_Laser_VCSEL_LIV_inTriggerModel” Uses a trigger model but is slower than “Pulse_Laser_VCSEL_LIV_inTriggerModel” which is used by default.

## Required Modules
1 x MSMU60-2

## Available Languages
* TSP
* Python

## Instructions
1. Adjust parameters and run code