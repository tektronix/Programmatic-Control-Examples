# Demonstrating Output Sequencing of Multiple Channels

Times turning output on and off from multiple channels with accurate delays utilizing trigger models.

The code is currently configured to work with two PSU modules and four channels. The current test setup includes the following delays:
On Delays
* `onDelay[0]= 0`
* `onDelay[1] = 0.005`
* `onDelay[2] = 0.010`
* `onDelay[3] = 0.015`

Off Delays
* `offDelay[0] = 0.015`
* `offDelay[1] = 0.010`
* `offDelay[2] = 0.005`
* `offDelay[3] = 0.0000`
These values can be updated at the bottom of the TSP file. Additionally, if you decide to include additional modules and channels, make sure to update the enable channel section accordingly. The enables list sets all channels to enabled by default. To disable just set the value at the corresponding index to false. For example, to disable channel one of slot one: `enables[0] = False`

## Required Modules
2 x MPSU50-2ST

## Available Languages
* TSP
* Python
* Python calling loaded TSP Scripts

## Instructions
1. Adjust settings as needed and run code. 
