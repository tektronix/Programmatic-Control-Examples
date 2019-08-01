# Date: 9/02/2015
#
# Using a raw socket connection to the web server (eScope) you can retrieve
# a PNG image of the screen.  There is no documentation on this, there
# probably never will be and future firmware may change the behavior of
# eScope which this demonstration relies heavily on.
#
# YOU HAVE BEEN WARNED!
#
# Tested On
# DPO4102 v2.30
# DPO4104 v2.68
# TDS3054B v3.41
# TDS3054C v4.05
#
# Should work on any eScope enabled instrument.

import socket, re, time # STD Py Modules


def GetScopeImage(ipAddress):
    input_buffer = 32 * 1024

    # Open a connection to the instrument's webserver
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ipAddr, 80))

    cmd = b"GET /image.png HTTP/1.0\n\n"
    s.send(cmd)

    # Get the HTTP header
    status = s.recv(input_buffer)

    #Read the first chunk of data
    data = s.recv(input_buffer)

    # Check if the content is a png image
    if (b"Content-Type: image/png" not in data):
        # Not proper data
        print("Content returned is not image/png")
        imgData = b""
        
    else: # Content is correct so copy the data to a file

        # Find the length of the png data
        searchObj = re.search(b"Content-Length: (\d+)\r\n", data)
        imgSizeLeft = int(searchObj.group(1))
        
        # Pull the image data out of the first buffer
        startIdx = data.find(b"\x89PNG")
        
        # For the TDS3000B Series, the PNG image data may not come out with the
        # HTTP header
        # If the PNG file header was not found then do another read
        if (startIdx == -1):
            data = s.recv(input_buffer)
            imgData = data[data.find(b"\x89PNG"):]
        else:
            imgData = data[startIdx:]
            
        imgSizeLeft = imgSizeLeft - len(imgData)

        # Read the rest of the image data
        data = s.recv(input_buffer)

        while imgSizeLeft > len(data):
            imgData = b"".join([imgData, data])
            imgSizeLeft = imgSizeLeft - len(data)
            data = s.recv(input_buffer)

            # The TDS3000B Series sends the wrong value for Content-Length.  It
            # sends a value much larger than the real length.
            # If there is no more data then break out of the loop
            if (len(data) == 0):
                break

        # Add the last chunk of data
        imgData = b"".join([imgData, data])

    # Close the connection
    s.close()

    return imgData

#============
# Start Here
#============

if __name__ == "__main__":
    #  Adjust these variables as necessary
    ipAddr = "192.168.1.5"
    save_file_location = 'C:\Data\{0}.png'.format(time.strftime("%Y%m%d_%H%M%S"))

    # Get the scope image data
    scopeShot = GetScopeImage(ipAddr)

    # Save the scope image data to a file
    saveFile = open(save_file_location, "wb")
    saveFile.write(scopeShot)
    saveFile.close()

    if len(scopeShot) > 0:
        print("Collected image successfully.")
        print("Image saved to {}".format(save_file_location))
        print("Size (bytes): {}".format(len(scopeShot)))


