# tekwfm.py usage examples

import time
import matplotlib.pyplot as plt # https://matplotlib.org/
import numpy as np #
import tekwfm

def demo1(myfile):
    """print date of trigger and plot scaled wfm 'myfile'"""
    volts, tstart, tscale, tfrac, tdatefrac, tdate = tekwfm.read_wfm(myfile)
    # print trigger time stamp
    print('local trigger time for: {}'.format(myfile))
    print('trigger: {}'.format(time.ctime(tdate)))
    # create time vector
    toff = tfrac * tscale
    samples, frames = volts.shape
    tstop = samples * tscale + tstart
    t = np.linspace(tstart+toff, tstop+toff, num=samples, endpoint=False)
    # plot 
    plt.figure(1)
    plt.axvline(linewidth=1, color='r') # trigger annotation
    plt.plot(t, volts)
    plt.xlabel('time (s)')
    plt.ylabel('volts (V)')
    plt.title('single waveform')
    plt.show()

def demo2(myfile):
    """plot frame 0 vs all frames on a two plot figure with locked time axes"""
    volts, tstart, tscale, tfrac, tdatefrac, tdate = tekwfm.read_wfm(myfile)
    # print trigger time stamps
    print('local trigger times for: {}'.format(myfile))
    for frame, utcseconds in enumerate(tdate):
        print('frame: {:02d}, trigger: {}'.format(frame, time.ctime(utcseconds)))
    # create time vector
    samples, frames = volts.shape
    tstop = samples * tscale + tstart
    t = np.linspace(tstart, tstop, num=samples, endpoint=False)
    # fractional trigger
    times = np.zeros(volts.shape)
    for frame, subsample in enumerate(tfrac):
        toff = subsample * tscale
        times[:,frame] = t + toff
    # plot: fastframe
    plt.figure(2)
    ax1 = plt.subplot(2, 1, 1)
    ax1.axvline(linewidth=1, color='r') # trigger annotation
    ax1.plot(times[:,0], volts[:,0])
    plt.ylabel('volts (V)')
    plt.title('only frame 1')
    ax2 = plt.subplot(2, 1, 2, sharex=ax1)
    ax2.axvline(linewidth=1, color='r') # trigger annotation
    ax2.plot(times, volts)
    plt.xlabel('time (s)')
    plt.ylabel('volts (V)')
    plt.title('all frames')
    plt.show()

def demo3(myfile):
    """plot fastframe record on continuous time scale.
not very practical for high frame counts or large delays between triggers"""
    volts, tstart, tscale, tfrac, tdatefrac, tdate = tekwfm.read_wfm(myfile)
    # create time vector
    samples, frames = volts.shape
    tstop = samples * tscale + tstart
    t = np.linspace(tstart, tstop, num=samples, endpoint=False)
    # fractional trigger
    times = np.zeros(volts.shape)
    for frame, subsample in enumerate(tfrac):
        toff = subsample * tscale
        times[:,frame] = t + toff
    # scale trigger times to first frame
    ref_frame = 0
    tdate -= tdate[ref_frame]
    tdatefrac -= tdatefrac[ref_frame]
    # the following operation reduces resolution
    # this may not be suitable for high frame counts
    # or acquisitions with large delays between triggers
    tdateall = tdate + tdatefrac
    times += tdateall # shift sample times
    # plot
    plt.figure(3)
    plt.plot(times, volts)
    plt.xlabel('time (s)')
    plt.ylabel('volts (V)')
    plt.title('all frames, continuous time')
    plt.show()

def demo4(myfile):
    """plot bar chart of time between frames"""
    volts, tstart, tscale, tfrac, tdatefrac, tdate = tekwfm.read_wfm(myfile)
    samples, frames = volts.shape
    x = np.arange(1, frames)
    iseconds = np.diff(tdate)
    fseconds = np.diff(tdatefrac)
    # the following operation reduces resolution
    # this may not be suitable for high frame counts
    # or acquisitions with large delays between triggers
    fseconds += iseconds
    # bar plot
    plt.figure(4)
    plt.bar(x, fseconds)
    #plt.xticks(x)
    plt.xlabel('diff(frame)')
    plt.ylabel('time (s)')
    plt.title('time between frames')
    plt.show()

