# PPG Examples
Original Attribution: Carl M - Tektronix Applications



## ppg_simple_example.py: 
A simplistic example of PPG communication and control.



## ppg_user_pattern_example.py:
Demonstration of the digital[1|2|3|4]:pattern:data and digital[1|2|3|4]:pattern:hdata commands for uploading user pattern data to the PPG.



## ppg_user_pattern_long_example.py:
PPG maximum record is 4,194,304 bits for a one-channel instrument and 2,097,152 bits for a two-channel or four-channel instrument. Long patterns require slicing into multiple write calls. This example demonstrates efficient division of a long user pattern.
<!-- markdown-link-check-disable -->
Resources
---------
Original Discussions:
+ https://forum.tek.com/viewtopic.php?f=580&t=141266
+ https://forum.tek.com/viewtopic.php?f=580&t=141267
+ https://forum.tek.com/viewtopic.php?f=580&t=141268
