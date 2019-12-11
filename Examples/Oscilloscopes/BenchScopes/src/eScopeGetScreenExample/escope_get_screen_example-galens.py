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

    if scopeShot:
        print("Collected image successfully.")
        print("Image saved to {0}".format(save_file))
        print("Size (bytes): {0}".format(len(scopeShot)))

