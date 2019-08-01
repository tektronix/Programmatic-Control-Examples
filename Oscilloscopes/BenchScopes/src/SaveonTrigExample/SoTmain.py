"""
Save on Trigger intended for Bench scopes.

Tested with DPO3054, MSO2024, TDS2024B, TDS3054B,
TDS2024C, DPO4032
Used USB and TCPIP Connections for the DPO scopes
Requires either TekVISA or NI-VISA installation
python 2.7 (http://www.python.org/)
pyvisa 1.3 (http://pypi.python.org/pypi/PyVISA/1.3)
To change the file path edit the saveontrig.dat
file found in the directly where USBsaveontrig resides.
"""
import sys
import struct
import os
from visa import *
from pyvisa import vpp43
from time import *
from struct import unpack

def main():
    #Initiate capture log
    capturelog = []

    # get path for files to be saved in, base file name and file format from
    # config.dat file.  Create a generic config.dat file if non exists
    if os.path.exists('saveontrig.dat') == False:
        f = open ('saveontrig.dat', 'w')
        f.write ('C:\Images\\')
        f.close()
    
    f = open ('saveontrig.dat', 'r')
    filepath = f.read() +  str(time()).split('.')[0] + '\\'
    f.close()
       
    #check if the directory for saved files is created, if not make it
    if not os.path.exists(filepath):
        os.makedirs(filepath)
        print 'Creating Directory ' + filepath            
    print "Capture data and logs will be saved to " + filepath
    print "To change the root directory for captured files"
    print "edit the saveontrig.dat file located in the folder where"
    print "SaveonTrig program resides."
    
    # Create list of VISA objects and allow user to select which to connect to
    resource_names = []
    while True:
        try:
            find_list, return_counter, instrument_description = \
                  vpp43.find_resources(resource_manager.session, "?*")
            resource_names.append(instrument_description)
            break
        except VisaIOError:
            print "No Instruments Detected"
            a = raw_input("Press ENTER to exit")
            raise SystemExit()
        except:
            print "Unable to communicate with VISA Driver"
            a = raw_input("Press ENTER to exit")
            raise SystemExit()
        
    for i in xrange(return_counter - 1):
        resource_names.append(vpp43.find_next(find_list))
    
    print "\nVisa resources found:"
    for a in range(len(resource_names)):
        print a, resource_names[a] 
    print "Attempting to Identify Instruments. Please Wait..."

    resource_ids = []
    for a in range(len(resource_names)):
        interface_type, _ = \
        vpp43.parse_resource(resource_manager.session, resource_names[a])
        if interface_type == VI_INTF_ASRL:
            resource_ids.append("RS232 not Supported")
        else:
            while True:
                try:
                    tempscope = instrument(resource_names[a], timeout = 10)
                    scopename = tempscope.ask("*IDN?")
                    scopename = scopename.split(',')
                    resource_ids.append(scopename[0] + '-' + scopename[1] + \
                                        ' ' + scopename[2])
                    break
                except VisaIOError:
                    resource_ids.append(" No Instrument Found ")
                    break
                except:
                    resource_ids.appent(" Error Communicating with this device")
            del tempscope
    
    print "\nIdentified Instruments:"
    for a in range(len(resource_names)):
        print a, resource_ids[a]
        
    # Query from user which scope to connect to
    while True:
        try:
            user_device = int(raw_input("Connect to which scope? \n"))
            if user_device in range(len(resource_names)):
                break
            else:
                print "Invalid Input, Please Try Again"
        except ValueError:
            print "Invalid Input, Please Try Again"
              
    
    # Connect to scope, and verify that it can be talked too      
    while True:
        try:
            scope = instrument(resource_names[user_device], timeout = 15)
            scopename = scope.ask("*IDN?")
            print scopename
            scopename = scopename.split(',')
            break
        except:
            print "Unable to communicate over this port"
            a = raw_input("Press ENTER to exit")
            raise SystemExit()
            
    
    # query from the user what type of capture to make
    while True:
        try:
            print "\n# Mode"
            print "0 HardCopy - Saves PNG, BMP or TIF images depending on scope"
            print "1 CSV - Savess waveform as a CSV file, viewable in Wavestar."
            print "2 Save both CSV and HardCopy"
            logmode = int(raw_input("Log which information? \n"))
            if logmode in range(3):
                break
            else:
                print "Invalid Input, Please Try Again"
        except ValueError:
            print "Invalid Input, Please Try Again"
    
    # query from the user how many minutes to capture data for
    while True:
        try:
            duration_time = float(raw_input("How many minutes should I run? \n"))
            break
        except ValueError:
            print "Invalid Input, Please Try Again"
    
    # Query from user if a trigger should be forced to execute periodically
    print "If no trigger is reieved, would you like to"
    Forcetrig = str(raw_input(" periodically force a trigger? (Y/N) \n"))
    if ('Y' in Forcetrig) or ('y' in Forcetrig):
        Forcetrig = True
        while True:
            try:
                Forcetrig_time = float(raw_input("How many seconds should I " \
                                        +"wait before forcing a trigger? \n"))
                break
            except ValueError:
                print "Invalid Input, Please Try Again"
    else:
        Forcetrig = False
    
    # Save current scope configuration
    print "Saving current scope setup."
    Scopesetup = scope.ask("*LRN?")
    # Determine the type of scope, and configure hard copy accordingly
    # And settings for aquiring the curve data
    if 'TDS' in scopename[1] and  '20'  in scopename[1]:
        fileformat = 'TIF'
        scope.write("header off")
        scope.write("HARDCOPY:BUTTON SAVESIMAGE")
        scope.write("HARDCOPY:FORMAT TIFF")
        scope.write("HARDCOPY:PORT USB")
        scope.write("wfmoutpre:bit_nr 8")
        Hscale = float(scope.ask("HOR:SCA?"))
        HDelay = float(scope.ask("HORizontal:DELay:POSITION?"))
        HPos = float((Hscale * 5 + float(scope.ask("HORIZONTAL:POSITION?")))/ \
                     (Hscale * 10) * 100)
    elif 'DPO' in scopename[1] or 'MSO' in scopename[1]:
        fileformat = 'PNG'
        scope.write(":header off")
        scope.write("wfmoutpre:bit_nr 8")
        Hscale = float(scope.ask("HOR:SCA?"))
        HDelay = float(scope.ask("HORizontal:DELay:TIMe?"))
        HPos = float(scope.ask("HORIZONTAL:POSITION?"))
        if '20' in scopename[1]:
            if str(scope.ask("DATA:COMP?")) != "COMPOSITE_YT":
                scope.write("DATA:COMP COMPOSITE_YT")
                print "Only Composite_YT supported for FilterVu"
                
    elif 'TDS' in scopename[1] and '30' in scopename[1]:
        fileformat = 'BMP'
        scope.write("header off")
        scope.write("HARDCOPY:PORT GPIB")
        scope.write("HARDCOPY:FORMAT BMPColor")
        scope.write("wfmoutpre:bit_nr 8")
        Hscale = float(scope.ask("HOR:SCA?"))
        HDelay = float(scope.ask("HORizontal:DELay:TIME?"))
        HPos = float((Hscale * 5 + float(scope.ask("HORIZONTAL:DELay:TIME?")))/ \
                     (Hscale * 10) * 100)
    
    #Generic all model configure the scope hardcopy settings
    scope.write("VERBOSE OFF")
    
    scope.write("HARDCOPY:LAYOUT PORTRAIT;PREVIEW 0;INKSAVER 0")
    scope.write("HARDCOPY:PALETTE NORMAL")
    scope.write("SAVE:IMAG:FILEF " + fileformat)
    recLen = scope.ask("horizontal:recordlength?")
    scope.write("data:start 1;stop " + recLen + \
                ";:data:encdg rpbinary;:DESE 1;:*ESE 1");
    scope.write("wfmoutpre:bit_nr 8")
    recLenNumBytes = len(recLen)
    headerLen = 1 + 1 + recLenNumBytes;
    xincr = float(scope.ask("wfmpre:xincr?"))
    ymult = float(scope.ask("wfmpre:ymult?"))
    yoff = float(scope.ask("wfmpre:yoff?"))
    yzero = float(scope.ask("wfmpre:yzero?"))
    
    # Determine which channels are enabled for
    if 'TD' in scopename[1]:
        if '4' in scopename[1][7]:
            channelson = range(4)
        if '2' in scopename[1][7]:
            channelson = range(2)
    else:    
        if '4' in scopename[1][6]:
            channelson = range(4)
        if '2' in scopename[1][6]:
            channelson = range(2)

    # Set up the sub folder for aquired data 
    filenumber = 1
    filename = scopename[1] + '_' + scopename[2] +'_'
    
        
    #Query from user of the front panel should be locked during operation
    print "Would you like to lock the front-panel during the capture session?"
    LockFP = str(raw_input())
    if (('Y' in LockFP) or ('y' in LockFP)):
        LockFP = True
        scope.write("LOCK ALL")
        capturelog.append("Front-panel locked during session? (Y/N)\n")
    else:
        LockFP= False
    
    # Start entering data into the capture log.  
    capturelog.append("Log for captures Starting Catpures on " + ctime()+ '\n')
    capturelog.append("Tracking " + str(scopename[1]) + " for " + \
                      str(duration_time) + " minutes. \n \n")
    
    # Determine which channels are actually on and record to the caputre log
    for a in channelson:
        channelson[a]=int(scope.ask("SEL:CH"+ str(a+1) +"?"))
        if channelson[a] == 1:
            print 'Channel ' + str(a+1) + ' is on'
            capturelog.append('Channel ' + str(a+1) + ' is on \n')
    
            
    # Acquire screen shots for duration of time indicated
    scope.write("ACQ:STOPA SEQ")
    print "Starting Catpures on " + ctime() + '\n'
    end_time = time() + (duration_time * 60)
    while time() < end_time:
        scope.write("ACQ:STATE RUN")
        waiting = 1
        looptime = time()
        # wait here until trigger received, forced trigger occurs or time ends
        while (waiting == 1):
            waiting = int(scope.ask("ACQ:STATE?"))
            #capture the trigger time
            if waiting == 0:
                triggertime = time()
            if looptime > end_time:
                if scope.ask("TRIGGER:STATE?") == 'READY':
                    print "No trigger event for finale capture" 
                          
                    capturelog.append('\n' "No trigger event for final capture" \
                                      + '\n')
                    break
            if Forcetrig:
                if (looptime + Forcetrig_time) < time():
                    triggertime = time()
                    scope.write("Trigger Force")
                    print "Trigger forced at " + str(ctime(triggertime)) +'\n'
                    capturelog.append("Trigger forced at " + \
                                      str(ctime(triggertime)) +'\n')
                    while (scope.ask("TRIGGER:STATE?") != 'SAV'):
                        scope.write("Trigger Force") # allows for Averageing to be used                    
                    break
                
        # Curve data captured and saved as CSV file        
        if (logmode == 1 or logmode == 2) and scope.ask("TRIGGER:STATE?") \
           != 'READY':
            for a in range(len(channelson)):
                if channelson[a] == 1:
                    scope.write("DATA:SOURCE CH" + str(a+1))
                    scope.write("CURVE?")
                    datac = scope.read_raw()
                    #If FP not locked, settings may have changed
                    if LockFP == False:
                        recLen = scope.ask("horizontal:recordlength?")
                        scope.write("data:start 1;stop " + recLen + \
                                    ";:data:encdg rpbinary;:DESE 1;:*ESE 1");
                        scope.write("wfmoutpre:bit_nr 8")
                        recLenNumBytes = len(recLen)
                        headerLen = 1 + 1 + recLenNumBytes;
                        xincr = float(scope.ask("wfmpre:xincr?"))
                        ymult = float(scope.ask("wfmpre:ymult?"))
                        yoff = float(scope.ask("wfmpre:yoff?"))
                        yzero = float(scope.ask("wfmpre:yzero?"))
                        if 'TDS' in scopename[1] and  '20'  in scopename[1]:
                            Hscale = float(scope.ask("HOR:SCA?"))
                            HDelay = float(scope.ask("HORizontal:DELay:" \
                                                     +"POSITION?"))
                            HPos = float((Hscale * 5 + float(scope.ask\
                                        ("HORIZONTAL:POSITION?")))/ \
                                        (Hscale * 10) * 100)
                        elif 'DPO' in scopename[1] or 'MSO' in scopename[1]:
                            Hscale = float(scope.ask("HOR:SCA?"))
                            HDelay = float(scope.ask("HORizontal:DELay:TIMe?"))
                            HPos = float(scope.ask("HORIZONTAL:POSITION?"))
                        elif 'TDS' in scopename[1] and '30' in scopename[1]:
                            Hscale = float(scope.ask("HOR:SCA?"))
                            HDelay = float(scope.ask("HORizontal:DELay:TIME?"))
                            HPos = float((Hscale * 5 + float(scope.ask\
                                                             ("HORIZONTAL:DELay"\
                                                              +":TIME?")))/ \
                                                             (Hscale * 10) * 100)

                    
                    # Strip the header
                    datac = datac[headerLen:(int(recLen)-1)]
                    # Convert to byte values
                    datac = unpack('%sB' % len(datac),datac)
                    # Convert bytes to voltage values
                    x = []
                    y = []
                    for i in range(0,len(datac)):
                        x.append((i-(len(datac)*(HPos/100)))* xincr + HDelay)
                        y.append(((datac[i]-yoff) * ymult) + yzero)
                    #save curve data in .csv format
                    f2 = open(filepath + filename+str(filenumber)+ ' CH_' \
                              + str(a+1)+'.csv', 'w')
                    f2.write("s,Volts\n")
                    for i in range(0,len(datac)):
                        f2.write(str(x[i]) + ',' + str(y[i])+ '\n')
                    f2.close()
                    print "CH " + str(a+1) + " Waveform #" + str(filenumber) \
                          + " saved as " + filepath + filename + str(filenumber)\
                          + ' CH_' + str(a+1)+ '.csv'  
                    print "     triggered at "+ ctime(triggertime) + '\n'
                    capturelog.append("CH " + str(a+1) + " Waveform #" \
                                      + str(filenumber)+ " saved as " \
                                      + filepath + filename + str(filenumber)\
                                      + ' CH_' + str(a+1)+ '.csv')
                    capturelog.append(" triggered at "+ ctime(triggertime) \
                                      + '\n')
    
        # start the data tansfer and save file for the Image format    
        if (logmode == 0 or logmode == 2) and scope.ask("TRIGGER:STATE?") \
           != 'READY':
            # Give some time for meas values to compute if no curve data pulled.
            if logmode == 0:
                sleep(.25)
            while True:
                try:
                    scope.write("HARDCOPY START")
                    sleep(.01)
                    data = scope.read()
                    scope.ask('*OPC?')
                    break
                except VisaIOError:
                    print "***Hard copy did not terminate correctly for " \
                          + str(filenumber) + "***"
                    print"    However the image may still be OK"
                    capturelog.append("***Hard copy did not terminate correctly" \
                                      " for " + str(filenumber) + "*** \n")
                    capturelog.append("   However the image may still be OK \n")
                    break
            #Save the hardcopy data as a image file
            f = open(filepath + filename+str(filenumber)+'.'+ fileformat \
                     , 'wb')
            f.write(data)
            f.close()
            print "HardCopy #" + str(filenumber) + " saved as " \
                  + filepath + filename + str(filenumber) + '.'+ \
                  fileformat  
            print "     triggered at "+ ctime(triggertime) + '\n'
            capturelog.append("HardCopy #" + str(filenumber) + " saved as " \
                  + filepath + filename + str(filenumber) + '.'+ \
                  fileformat )
            capturelog.append(" triggered at "+ ctime(triggertime) + '\n')
    
        #increment the capture number       
        filenumber = filenumber + 1
    
    #clean up after captures complete, and write the capture log to a file
    print "Completed catpures on " + ctime()+ '\n'
    if LockFP:
        scope.write("LOCK NONE")
        print "Unlocking Front-panel controlls."
    capturelog.append('\n' + "Completed all on " + ctime()+ '\n')
    # Save capture log to file
    caplogfile = filepath + "Capture_Log_" + str(int(time())) + ".txt"
    print "Saving Capture Log to " + caplogfile
    f3 = open(caplogfile, 'w')
    for a in range(len(capturelog)):
        f3.write(capturelog[a])
    f3.write("Initial scope setup:\n")
    f3.write(Scopesetup)
    f3.close()
    scope.write(Scopesetup)
    print "Done"

