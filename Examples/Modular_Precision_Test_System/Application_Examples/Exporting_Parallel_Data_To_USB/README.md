# Exporting Parallel Measurements to USB Drive 

This script performs long term datalogging for parallel resistance measurements. The test can be stopped by the user occasionally to export measurements to a USB drive. 

There are two primary methods for parallel measurement provided in this script. The simpler and more accurate method utilizes a trigger timer. This sends an event to all channels notifying them to take a measurement. The second method uses delay constants. This is more complex and less accurate (.33us drift every iteration), however, it provides a look into how multiple trigger models can communicate and interact. This script is not designed for very fast measurements (<1ms), there are other methods that can be used to achieve such timing.

## Required Modules
2 or 3 x MSMU60-2

## Available Languages
* TSP

## Instructions
1. Begin by connecting to the mainframe using the instrument panel found on the left side of the visual studio code interface or running the TSP: Connect function and entering the IP address or VISA resource screen.
2. Update the scan parameters according to your device’s specifications.
3. There are three functions designed for user use: “start_scan()”, “pause_export_resume()”, and “end_scan()”. 
* “start_scan()” will begin measuring across all channels according to your parameters.
* “pause_export_resume()” will abort all measuring, export resistance data from buffers to a USB drive connected to the front panel, then continue measuring.
* “end_scan()” will end the measurements without exporting to USB.
4. Connect sensors/resistive loads to all channels. The script is designed to work with an even number of channels. If using an odd number of channels simply do not connect the final channel. 
5. When the script is run, it will begin measuring across all channels. Intermittently the user may want to export previous data to a USB. This can be done by sending “pause_export_resume()” to the mainframe through the TSP terminal. 
