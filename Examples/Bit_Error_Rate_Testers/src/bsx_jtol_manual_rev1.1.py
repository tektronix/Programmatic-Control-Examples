# SCPI JTOL BSA/BSX script
# joseph.swelland@tektronix.com 8/1/2019

# Pre-reqs: set BSX remote client terminator to 'LF', good setup file recalled, loopback verified

import socket
import time
import numpy

class TekBertError(Exception):
    '''base error class for SocketInstrClass class'''
    pass

class TekBertClass(object):
    '''generic class for raw socket control'''
    def __init__(self, host='192.168.0.58', port=23, timeout=10.0):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(0)
        self.socket.settimeout(timeout) # seconds
        self.socket.connect((host, port))

    def disconnect(self):
        '''closes connection'''
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def query(self, cmd):
        '''returns a reply as string'''
        c = '{}\n'.format(cmd)
        self.socket.send(c.encode('latin_1'))
        r = self.socket.recv(4096)
        while (r[-1] != 10):
            r += self.socket.recv(4096)
        return r.decode('latin_1').strip()

    def write(self, cmd):
        '''write cmd with status check option'''
        c = '{}\n'.format(cmd)
        b = self.socket.send(c.encode('latin_1'))
        r = self.query('rst?')
        return None

if __name__ == "__main__":

    #test - can be removed
    bsx = TekBertClass(host='10.233.16.189', port=23)
    r = bsx.query('*IDN?')
    print(r)

    # results
    t = numpy.zeros(7, dtype=([('Freq',int),('SJ',float),('BITS * 10E9',float),('ERRORS',int),('BER',float),('ReSyncs', int)]))
    
    # --------------------------------------------------------------------------------------------    
    # 500kHz
    bsx.write('RST 0')  # stop BERT if running
    bsx.write('view DETECTOR')  # switch view to detector
    bsx.write('detector:resetall')  # reset detector

    #setup
    r = int(bsx.query('DETector:ETIMe?'))  #how long has BERT been running?
    e = 0 # variable for number of errors
    settle = 0  # variable for time (sec) after an SJ change where errors are ignored
    rest = 0  # variable for SJ soak time
    iup = 50  # SJ increase step % <user set value>
    idwn = 5  # SJ decrease step % <user set value>
    sj = 100  # starting SJ % <user set value>

    bsx.write('GSM:SJitter:FREQuency %6d' % 500000)  #set SJ freq to 500kHz
    bsx.write('GSM:SJitter:AMPUi %3d' % sj)  #set SJ amplitude to start value, 100% for 500kHz
    bsx.write('RST 1')  #run BERT

    while (r<167):  # run JTOL for 167 seconds, 95% confidence at 1E-12 BER for 32Gb/s
        if (rest):  # we are getting errors, now need to step down SJ
            e = int(bsx.query('DETector:ERRors?'))  # query number of errors
            if (e>3): # reduce SJ by idwn
                r = bsx.query('GSM:SJitter:AMPUi?').split()
                sj = float(r[0]) - idwn
                bsx.write('GSM:SJitter:AMPUi %3d' % sj)       
                bsx.write('DETector:RESetall')
        else: # if any errors within first 10 sec, clear DET and start again
            while (r<30):
               if (e>0 and r<10 and settle==0):
                   bsx.write('DETector:RESetall')
                   settle = 1
               elif (e>0):
                   break

               r = int(bsx.query('DETector:ETIMe?'))
               e = int(bsx.query('DETector:ERRors?'))
                
            if (e<1): # incrementing SJ by iup
               r = bsx.query('GSM:SJitter:AMPUi?').split()
               sj = float(r[0]) + iup
               bsx.write('GSM:SJitter:AMPUi %3d' % sj)       
               bsx.write('DETector:RESetall')
               settle = 0
            else:
                rest = 1 # means we are getting errors, need to reduce SJ

        r = int(bsx.query('DETector:ETIMe?'))
                    
    bsx.write('RST 0')        #stop the BERT   
    # save results
    t[0]['Freq'] = 500000
    r = bsx.query('GSM:SJitter:AMPUi?').split()
    t[0]['SJ'] = float(r[0])
    t[0]['BITS * 10E9'] = (float(bsx.query('DETector:BITS?')) / (10**9))
    t[0]['ERRORS'] = int(bsx.query('DETector:ERRORS?'))
    t[0]['BER'] = t[0]['ERRORS']/(t[0]['BITS * 10E9'] * pow(10,9))
    t[0]['ReSyncs'] = int(bsx.query('DETector:RESYncs?'))
        
    # --------------------------------------------------------------------------------------------                 
    # 1MHz
    bsx.write('RST 0')
    bsx.write('view DETECTOR')
    bsx.write('detector:resetall')

    #setup
    r = int(bsx.query('DETector:ETIMe?'))
    e = 0
    settle = 0
    rest = 0
    iup = 50
    idwn = 5
    sj = 100

    bsx.write('GSM:SJitter:FREQuency %6d' % 1000000)
    bsx.write('GSM:SJitter:AMPUi %3d' % sj)
    bsx.write('RST 1')

    while (r<167):
        if (rest):
            e = int(bsx.query('DETector:ERRors?'))
            if (e>3):
                r = bsx.query('GSM:SJitter:AMPUi?').split()
                sj = float(r[0]) - idwn
                bsx.write('GSM:SJitter:AMPUi %3d' % sj)       
                bsx.write('DETector:RESetall')
        else:
            while (r<30):
               if (e>0 and r<10 and settle==0):
                   bsx.write('DETector:RESetall')
                   settle = 1
               elif (e>0):
                   break

               r = int(bsx.query('DETector:ETIMe?'))
               e = int(bsx.query('DETector:ERRors?'))
                
            if (e<1):
               r = bsx.query('GSM:SJitter:AMPUi?').split()
               sj = float(r[0]) + iup
               bsx.write('GSM:SJitter:AMPUi %3d' % sj)       
               bsx.write('DETector:RESetall')
               settle = 0
            else:
                rest = 1

        r = int(bsx.query('DETector:ETIMe?'))
                    
    bsx.write('RST 0')           
    # save results
    t[1]['Freq'] = 1000000
    r = bsx.query('GSM:SJitter:AMPUi?').split()
    t[1]['SJ'] = float(r[0])
    t[1]['BITS * 10E9'] = (float(bsx.query('DETector:BITS?')) / (10**9))
    t[1]['ERRORS'] = int(bsx.query('DETector:ERRORS?'))
    t[1]['BER'] = t[1]['ERRORS']/(t[1]['BITS * 10E9'] * pow(10,9))
    t[1]['ReSyncs'] = int(bsx.query('DETector:RESYncs?'))

    # -------------------------------------------------------------------------------------------- 
    # 5MHz
    bsx.write('RST 0')
    bsx.write('view DETECTOR')
    bsx.write('detector:resetall')

    #setup
    r = int(bsx.query('DETector:ETIMe?'))
    e = 0
    settle = 0
    rest = 0
    iup = 25
    idwn = 5
    sj = 50

    bsx.write('GSM:SJitter:FREQuency %6d' % 5000000)
    bsx.write('GSM:SJitter:AMPUi %3d' % sj)
    bsx.write('RST 1')

    while (r<167):
        if (rest):
            e = int(bsx.query('DETector:ERRors?'))
            if (e>3):
                r = bsx.query('GSM:SJitter:AMPUi?').split()
                sj = float(r[0]) - idwn
                bsx.write('GSM:SJitter:AMPUi %3d' % sj)       
                bsx.write('DETector:RESetall')
        else:
            while (r<30):
               if (e>0 and r<10 and settle==0):
                   bsx.write('DETector:RESetall')
                   settle = 1
               elif (e>0):
                   break

               r = int(bsx.query('DETector:ETIMe?'))
               e = int(bsx.query('DETector:ERRors?'))
                
            if (e<1):
               r = bsx.query('GSM:SJitter:AMPUi?').split()
               sj = float(r[0]) + iup
               bsx.write('GSM:SJitter:AMPUi %3d' % sj)       
               bsx.write('DETector:RESetall')
               settle = 0
            else:
                rest = 1

        r = int(bsx.query('DETector:ETIMe?'))
                    
    bsx.write('RST 0')           
    # save results
    t[2]['Freq'] = 5000000
    r = bsx.query('GSM:SJitter:AMPUi?').split()
    t[2]['SJ'] = float(r[0])
    t[2]['BITS * 10E9'] = (float(bsx.query('DETector:BITS?')) / (10**9))
    t[2]['ERRORS'] = int(bsx.query('DETector:ERRORS?'))
    t[2]['BER'] = t[2]['ERRORS']/(t[2]['BITS * 10E9'] * pow(10,9))
    t[2]['ReSyncs'] = int(bsx.query('DETector:RESYncs?'))

    # --------------------------------------------------------------------------------------------     
    # 10MHz
    bsx.write('RST 0')
    bsx.write('view DETECTOR')
    bsx.write('detector:resetall')

    #setup
    r = int(bsx.query('DETector:ETIMe?'))
    e = 0
    settle = 0
    rest = 0
    iup = 10
    idwn = 3
    sj = 25

    bsx.write('GSM:SJitter:FREQuency %6d' % 10000000)
    bsx.write('GSM:SJitter:AMPUi %3d' % sj)
    bsx.write('RST 1')

    while (r<167):
        if (rest):
            e = int(bsx.query('DETector:ERRors?'))
            if (e>3):
                r = bsx.query('GSM:SJitter:AMPUi?').split()
                sj = float(r[0]) - idwn
                bsx.write('GSM:SJitter:AMPUi %3d' % sj)       
                bsx.write('DETector:RESetall')
        else:
            while (r<30):
               if (e>0 and r<10 and settle==0):
                   bsx.write('DETector:RESetall')
                   settle = 1
               elif (e>0):
                   break

               r = int(bsx.query('DETector:ETIMe?'))
               e = int(bsx.query('DETector:ERRors?'))
                
            if (e<1):
               r = bsx.query('GSM:SJitter:AMPUi?').split()
               sj = float(r[0]) + iup
               bsx.write('GSM:SJitter:AMPUi %3d' % sj)       
               bsx.write('DETector:RESetall')
               settle = 0
            else:
                rest = 1

        r = int(bsx.query('DETector:ETIMe?'))
                    
    bsx.write('RST 0')           
    # save results
    t[3]['Freq'] = 10000000
    r = bsx.query('GSM:SJitter:AMPUi?').split()
    t[3]['SJ'] = float(r[0])
    t[3]['BITS * 10E9'] = (float(bsx.query('DETector:BITS?')) / (10**9))
    t[3]['ERRORS'] = int(bsx.query('DETector:ERRORS?'))
    t[3]['BER'] = t[3]['ERRORS']/(t[3]['BITS * 10E9'] * pow(10,9))
    t[3]['ReSyncs'] = int(bsx.query('DETector:RESYncs?'))

    # -------------------------------------------------------------------------------------------- 
    # 20MHz
    bsx.write('RST 0')
    bsx.write('view DETECTOR')
    bsx.write('detector:resetall')

    #setup
    r = int(bsx.query('DETector:ETIMe?'))
    e = 0
    settle = 0
    rest = 0
    iup = 10
    idwn = 1
    sj = 10

    bsx.write('GSM:SJitter:FREQuency %6d' % 20000000)
    bsx.write('GSM:SJitter:AMPUi %3d' % sj)
    bsx.write('RST 1')

    while (r<167):
        if (rest):
            e = int(bsx.query('DETector:ERRors?'))
            if (e>3):
                r = bsx.query('GSM:SJitter:AMPUi?').split()
                sj = float(r[0]) - idwn
                bsx.write('GSM:SJitter:AMPUi %3d' % sj)       
                bsx.write('DETector:RESetall')
        else:
            while (r<30):
               if (e>0 and r<10 and settle==0):
                   bsx.write('DETector:RESetall')
                   settle = 1
               elif (e>0):
                   break

               r = int(bsx.query('DETector:ETIMe?'))
               e = int(bsx.query('DETector:ERRors?'))
                
            if (e<1):
               r = bsx.query('GSM:SJitter:AMPUi?').split()
               sj = float(r[0]) + iup
               bsx.write('GSM:SJitter:AMPUi %3d' % sj)       
               bsx.write('DETector:RESetall')
               settle = 0
            else:
                rest = 1

        r = int(bsx.query('DETector:ETIMe?'))
                    
    bsx.write('RST 0')           
    # save results
    t[4]['Freq'] = 20000000
    r = bsx.query('GSM:SJitter:AMPUi?').split()
    t[4]['SJ'] = float(r[0])
    t[4]['BITS * 10E9'] = (float(bsx.query('DETector:BITS?')) / (10**9))
    t[4]['ERRORS'] = int(bsx.query('DETector:ERRORS?'))
    t[4]['BER'] = t[4]['ERRORS']/(t[4]['BITS * 10E9'] * pow(10,9))
    t[4]['ReSyncs'] = int(bsx.query('DETector:RESYncs?'))

    # -------------------------------------------------------------------------------------------- 
    # 50MHz
    bsx.write('RST 0')
    bsx.write('view DETECTOR')
    bsx.write('detector:resetall')

    #setup
    r = int(bsx.query('DETector:ETIMe?'))
    e = 0
    settle = 0
    rest = 0
    iup = 5
    idwn = 1
    sj = 10

    bsx.write('GSM:SJitter:FREQuency %6d' % 50000000)
    bsx.write('GSM:SJitter:AMPUi %3d' % sj)
    bsx.write('RST 1')

    while (r<167):
        if (rest):
            e = int(bsx.query('DETector:ERRors?'))
            if (e>3):
                r = bsx.query('GSM:SJitter:AMPUi?').split()
                sj = float(r[0]) - idwn
                bsx.write('GSM:SJitter:AMPUi %3d' % sj)       
                bsx.write('DETector:RESetall')
        else:
            while (r<30):
               if (e>0 and r<10 and settle==0):
                   bsx.write('DETector:RESetall')
                   settle = 1
               elif (e>0):
                   break

               r = int(bsx.query('DETector:ETIMe?'))
               e = int(bsx.query('DETector:ERRors?'))
                
            if (e<1):
               r = bsx.query('GSM:SJitter:AMPUi?').split()
               sj = float(r[0]) + iup
               bsx.write('GSM:SJitter:AMPUi %3d' % sj)       
               bsx.write('DETector:RESetall')
               settle = 0
            else:
                rest = 1

        r = int(bsx.query('DETector:ETIMe?'))
                    
    bsx.write('RST 0')           
    # save results
    t[5]['Freq'] = 50000000
    r = bsx.query('GSM:SJitter:AMPUi?').split()
    t[5]['SJ'] = float(r[0])
    t[5]['BITS * 10E9'] = (float(bsx.query('DETector:BITS?')) / (10**9))
    t[5]['ERRORS'] = int(bsx.query('DETector:ERRORS?'))
    t[5]['BER'] = t[5]['ERRORS']/(t[5]['BITS * 10E9'] * pow(10,9))
    t[5]['ReSyncs'] = int(bsx.query('DETector:RESYncs?'))

    # -------------------------------------------------------------------------------------------- 
    # 100MHz
    bsx.write('RST 0')
    bsx.write('view DETECTOR')
    bsx.write('detector:resetall')

    #setup
    r = int(bsx.query('DETector:ETIMe?'))
    e = 0
    settle = 0
    rest = 0
    iup = 3
    idwn = 1
    sj = 5

    bsx.write('GSM:SJitter:FREQuency %6d' % 100000000)
    bsx.write('GSM:SJitter:AMPUi %3d' % sj)
    bsx.write('RST 1')

    while (r<167):
        if (rest):
            e = int(bsx.query('DETector:ERRors?'))
            if (e>3):
                r = bsx.query('GSM:SJitter:AMPUi?').split()
                sj = float(r[0]) - idwn
                bsx.write('GSM:SJitter:AMPUi %3d' % sj)       
                bsx.write('DETector:RESetall')
        else:
            while (r<30):
               if (e>0 and r<10 and settle==0):
                   bsx.write('DETector:RESetall')
                   settle = 1
               elif (e>0):
                   break

               r = int(bsx.query('DETector:ETIMe?'))
               e = int(bsx.query('DETector:ERRors?'))
                
            if (e<1):
               r = bsx.query('GSM:SJitter:AMPUi?').split()
               sj = float(r[0]) + iup
               bsx.write('GSM:SJitter:AMPUi %3d' % sj)       
               bsx.write('DETector:RESetall')
               settle = 0
            else:
                rest = 1

        r = int(bsx.query('DETector:ETIMe?'))
                    
    bsx.write('RST 0')           
    # save results
    t[6]['Freq'] = 100000000
    r = bsx.query('GSM:SJitter:AMPUi?').split()
    t[6]['SJ'] = float(r[0])
    t[6]['BITS * 10E9'] = (float(bsx.query('DETector:BITS?')) / (10**9))
    t[6]['ERRORS'] = int(bsx.query('DETector:ERRORS?'))
    t[6]['BER'] = t[6]['ERRORS']/(t[6]['BITS * 10E9'] * pow(10,9))
    t[6]['ReSyncs'] = int(bsx.query('DETector:RESYncs?'))

    # -------------------------------------------------------------------------------------------- 
    # print results
    for j in range (0,7):
        print('Freq: %9d, SJ: %4f, BITS 10E9: %18.12f, ERRORS: %d, BER: %12s, ReSyncs: %3d' % (t[j]['Freq'], t[j]['SJ'], t[j]['BITS * 10E9'], t[j]['ERRORS'], t[j]['BER'], t[j]['ReSyncs']))
