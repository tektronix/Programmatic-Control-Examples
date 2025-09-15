
--OCP Demo Script

--This script is designed for an OCP (Over Current Protection) demo. 
--It sets the source voltage and current limit, configures the OCP and OVP 
--(Over Voltage Protection) values, and then turns on the PSU (Power Supply Unit).


-- UPDATE THE FOLLOWING
slotNumber = 2 -- The slot number where your PSU is located
slotChannel = 2 -- The channel you are using on your PSU

slot[slotNumber].psu[slotChannel].source.levelv = 15
slot[slotNumber].psu[slotChannel].source.limiti = 0.350
slot[slotNumber].psu[slotChannel].source.protect.leveli = 0.5
slot[slotNumber].psu[slotChannel].source.protect.levelv = 55

slot[slotNumber].psu[slotChannel].source.output = slot[slotNumber].psu.ON