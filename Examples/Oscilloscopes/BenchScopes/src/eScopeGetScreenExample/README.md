# eScope Socket Get Screen Shot Example
Original Attribution: Dave W. - Tektronix Applications

This example allows you to get a PNG screen shot image from eScope enabled oscilloscopes by reading it directly from the scope's web server. This example is based on the MATLAB example eScope MATLAB Socket Get Screen 1 that can also be found here on the forums.

This example was tested and confirmed to work on the following models:
• DPO4102 v2.30
• DPO4104 v2.68
• TDS3054B v3.41
• TDS3054C v4.05
This example should, in theory, work with any scope that has the eScope interface. However, future firmware may change the behavior of eScope which this example relies heavily on.



File: [escope_get_screen_example.py](./escope_get_screen_example.py)


# eScope Socket Get Screen Shot Example with python request library
Original Attribution: galens

 I have a TDS3014 (v3.41) connected to my local network over ethernet. Today I tried to get a screen shot using the scope's web interface. Using Firefox ESR 52.1.0, I got download failures. Using Chrome 58.0.3029.110, the web image of the screen doesn't even come up. I seem to recall encountering this same problem in the past couple of years, but I don't recall exactly when I ceased being able to download the image of the screen. Anyway, today I really wanted the screenshot. I found this posting and thought I'd give it a try. As is, the script didn't work for me, but thanks to the Python Requests library, I was able to modify the code to get it to work. The Requests library greatly simplifies the image download. I'm putting my code here in case others might find it useful.

```python
#!/usr/bin/env python
# Date: 2017-05-14
#
# Using the Python Requests library to communicate with the web server
# (eScope) you can retrieve a PNG image of the screen.  This is a
# hacked version of Dave W's example code from the Tektronix user
# forum.
#
# Tested On
# TDS3014 v3.41
#
# From Dave W's older code:
# "There is no documentation on this, there probably never will be and
# future firmware may change the behavior of eScope which this
# demonstration relies heavily on.
#
# YOU HAVE BEEN WARNED!
#
# ...snip...
#
# Should work on any eScope enabled instrument."


import requests
import os


def GetScopeImage(scope_name):
    r = requests.get('http://' + scope_name + '/image.png')
    return r.content


#============
# Start Here
#============

if __name__ == "__main__":
    #  Adjust these variables as necessary
    #scope_name = "scope.example.com"
    scope_name = "192.168.1.199"
    save_file_path = os.path.expanduser('~') + '/Downloads/'
    save_file_name = 'scope_shot.png'
    save_file = save_file_path + save_file_name

    # Get the scope image data
    scopeShot = GetScopeImage(scope_name)

    # Save the scope image data to a file
    saveFile = open(save_file, "wb")
    saveFile.write(scopeShot)
    saveFile.close()

    if len(scopeShot) > 0:
        print("Collected image successfully.")
        print("Image saved to {0}".format(save_file))
        print("Size (bytes): {0}".format(len(scopeShot)))

```



Resources
---------
Original Discussion:
https://forum.tek.com/viewtopic.php?f=580&t=138366

