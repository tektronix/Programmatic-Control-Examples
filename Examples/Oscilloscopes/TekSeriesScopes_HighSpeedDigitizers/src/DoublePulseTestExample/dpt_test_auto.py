# ***********************************************************************************************************
# * Copyright (c) Tektronix
# * ---------------------------------------------------------------------------------------------------------
# * Module Name:    dpt_test_auto.py
# * Module Type:    Python scripts
# * Module Rev:     1.0                         
# * Module Author:  ning.ai@tektronix.com
# * Module Input:   Refer to the "User input settings"
# * Module Output:  
# * Description:    A WBG-DPT automation test demo
# *                 Vgs, Vds and Id (3 signals) are requested.
# * Examples:       dpt_test_auto.py
# * ---------------------------------------------------------------------------------------------------------
# * Revision History
# * Date:		    2023-Aug-08
# * Notes:          First revision (v1.0)
# *                 Demo guildline
# *                 1. Connect MSO5/6B AFG output to AFG31000 trigger input;
# *                 2. Configure the AFG31000 double pulse settings manually;
# *                    The same settings (pulse_1_width ... pulse_2_gap) used in scripts
# *                 3. Connect the probes to the scope and finish the DPT setup;
# *                 4. Modify the user input settings in scripts;
# *                 5. Run the scripts to start the demo
# * ---------------------------------------------------------------------------------------------------------
# * Date:		    2023-Oct-10
# * Notes:          Revision v1.1
# *                 1. Add automatical control of AFG with DPT control interface;
# * ---------------------------------------------------------------------------------------------------------
# * Date:		    2024-Jan-31
# * Notes:          Revision v1.2
# *                 1. The stuck issue has been resolved;
# * ---------------------------------------------------------------------------------------------------------
# * Date:		    month/day/year    
# * Notes:
# ***********************************************************************************************************

# ----------------------------------------------------

# User input settings

# Oscilloscope IP address
scope_ip = '192.168.3.159'
afg_ip = '192.168.3.179'
visa_address_scope = 'TCPIP0::' + scope_ip + '::inst0::INSTR'
visa_address_afg = 'TCPIP0::' + afg_ip + '::inst0::INSTR'
# visa_address = 'USB::0x0699::0x0530::C031748::INSTR'
# If reset the scope
rst_scope_ena = 1
# Channel number, one of 1 - 8
# Set Vgs channel number
vgs_chn = 1
# Set Vds channel number
vds_chn = 2
# Set Id channel number
id_chn = 3
# Enable Id channel zero compenstation (E.g. Rogowski coil 0v offset)
# Enbale math channel for the Id calculation, 0 = disable math channel
# 1 = Math1, 2 = Math2, 3 = Math3, 4 = Math4
id_math_chn = 1
# If id_math_chn > 0, gating range for offset voltage calculation
# Relative location of entire record length.
# 0.0 to 0.1 means 0.0 * whole time span + time start to 0.1 * whole time span + time start
id_zero_gate_beg = 0.0
id_zero_gate_end = 0.05
# Define if enable Vgs channel invert, 1 = invert, 0 = non-invert
vgs_chn_invert = 0
# Define if enable Vgs channel invert, 1 = invert, 0 = non-invert
vds_chn_invert = 0
# Define if enable Id channel invert, 1 = invert, 0 = non-invert
id_chn_invert = 0
# Deskew of probes/channels (unit: second, -125ns to +125ns with 40ps resolution)
vgs_chn_deskew_sec = 0
vds_chn_deskew_sec = 0
id_chn_deskew_sec = 0
# Id alternate unit ratio setting 
# (if set to 0, disable Id channel alternate unit)
# (if not 0, set the channel alternate on and the ratio)
id_alt_unit_ratio = 0
# Sample rate, unit : sample/second (if set to 0, then use default setting 12.5GS/s)
sample_rate = 12.5e9
# Recond length, unit : sample/second (if set to 0, then it will be calculate from pulse width)
recond_length = 0
# Horizontal position, unit : % (if set to 0, then use scripts default setting 25, which means 25%)
horizontal_position = 0;
# AFG output amplitude with the high-z load mode (unit: volt)
afg_output_h = 5
afg_output_l = 0
# pulse width, unit : seconds, if recond_length > 0, those data won't be used
pulse_1_width = 5e-6
pulse_1_gap = 10e-6
pulse_2_width = 2e-6
pulse_2_gap = 10e-6
# if auto change veritcal settings
autoset_vertical_ena = 1
autoset_vgs_ena = 1
autoset_vds_ena = 0
autoset_id_ena  = 0
# Vgs voltage amplitude, unit : V
vgs_amplitude = 5
# Vds voltage amplitude, unit : V
vds_amplitude = 50
# Id current amplitude, unit : A
id_amplitude = 1
# Manual settings of vertical
# Scale unit: v/div or A/div, offset unit: v or A
vgs_scale_manual = 3.0
vgs_offset_manual = 0.0
vgs_position_manual = 0.0
vds_scale_manual = 10.0
vds_offset_manual = 0.0
vds_position_manual = 0.0
id_scale_manual = 5.0
id_offset_manual = 0.0
id_position_manual = 0.0
# Vertical amplitude margin ratio
vertical_margin_ratio_h = 0.95
vertical_margin_ratio_l = 0.85
vertical_autoset_ratio = 0.5
# Triger level, unit : V, set to 0 will use half of Vgs voltage
trig_lvl = 0
# Remote save (Save on the scope)
# If enable remote save
remote_session_save_ena = 0
remote_wfm_save_ena = 0
remote_screen_save_ena = 0
remote_table_save_ena = 0
# Make sure the path end up with "/"
path_scope = 'C:/Temp/WBG_DPT/'
session_name = 'double_pulse_test_demo'
result_table_name = 'result_table'
result_table_ext = '.csv'
screen_name = 'screen_capture'
screen_ext = '.png'
# local save (Save on the PC which is running the scripts)
local_wfm_save_ena = 1
local_table_save_ena = 1
# Make sure the path end up with "/"
path_local = 'C:/Temp/WBG_DPT/'
result_local_name = 'results.csv'
# Test iteration number
test_iter_num = 1
# Test iteration interval (unit: second)
# There is intrisic sleep time 4 seconds for each iteration.
# the final iteration interval will be 4 + test_iter_intvl seconds.
test_iter_intvl = 1
# Wait until the scope become free or time out
# The unit for the wait time in time out setting is second
acq_wait_timeout_time = 10

# ----------------------------------------------------
# import sys
# path_set = 'C:/Users/u619059/OneDrive - Fortive/Documents/scripts/python/projects/MSO6_ac_transfer_function'
# sys.path.append(path_set)
import os
import sys
import shutil
try:
    path_set
except NameError:
    path_set = os.getcwd()
else:
  	print('PATH： ' + path_set)


import pyvisa as visa
import numpy as np
# import matplotlib.pyplot as plt
import time
import csv

# ----------------------------------------------------
# Wait until the scope become free
def wait_for_scope_free():
    r = scope.query('BUSY?')
    busy_flag = int(r)
    while busy_flag != 0:
       r = scope.query('BUSY?')
       busy_flag = int(r)
       time.sleep(0.5)
       
# Wait until the scope become free or time out
# The unit for the wait time in time out setting is second
def wait_for_scope_free_timeout(time_wait):
    r = scope.query('BUSY?')
    busy_flag = int(r)
    for time_cnt in range(time_wait):
        if busy_flag != 0:
           r = scope.query('BUSY?')
           busy_flag = int(r)
           print('checking')
           time.sleep(1)
        else:
           break
    return busy_flag

# Wait until the acquistion status become stop or time out
# The unit for the wait time in time out setting is second
def wait_for_scope_acq_stop_or_timeout(time_wait):
    r = scope.query('ACQuire:STATE?')
    acq_status = int(r)
    for time_cnt in range(time_wait):
        if acq_status != 0:
           r = scope.query('ACQuire:STATE?')
           acq_status = int(r)
           print('checking')
           time.sleep(1)
        else:
           break
    return acq_status


# Wait until the AFG become free
def wait_for_afg_free():
    time.sleep(0.1)
    
def read_wfm_horizontal():
    record = int(scope.query('horizontal:recordlength?'))
    scope.write('WFMOutpre?')
    wdfout_bytes = scope.read_raw()
    wdfout_bytes_list = wdfout_bytes.split(b';')
    # print(wdfout_bytes_list[13])
    # print(wdfout_bytes_list[13].decode('ascii'))
    tscale = float(wdfout_bytes_list[11].decode('ascii'))
    tstart = float(wdfout_bytes_list[12].decode('ascii'))
    pt_offset = int(wdfout_bytes_list[13].decode('ascii'))
    # retrieve scaling factors
    #tscale = float(scope.query('wfmoutpre:xincr?'))
    #tstart = float(scope.query('wfmoutpre:xzero?'))
    # create scaled time vectors
    # horizontal (time)
    total_time = tscale * record
    tstop = tstart + total_time
    scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False)
    scaled_time = scaled_time - pt_offset * tscale
    return scaled_time

def read_wfm_vertical(chn):
    chn_str = 'CH' + str(chn)
    # io config
    scope.write('header 0')
    scope.write('data:encdg SRIBINARY')
    scope.write('data:source ' + chn_str)
    scope.write('data:start 1') # first sample
    record = int(scope.query('horizontal:recordlength?'))
    # print('Recond length: ' + str(record))
    scope.write('data:stop {}'.format(record)) # last sample
    scope.write('wfmoutpre:byt_n 2') # 1 byte per sample
    # Select channel to read
    print('Read channel wfm: ' + chn_str)
    # Query the waveform
    bin_wave = scope.query_binary_values('curve?', datatype='b', container=np.array)
    # print('Query waveform data')
    # Get vertical resolution
    vscale = float(scope.query('wfmoutpre:ymult?')) # volts / level
    voff = float(scope.query('wfmoutpre:yzero?')) # reference voltage
    vpos = float(scope.query('wfmoutpre:yoff?')) # reference position (level)
    # error checking
    r = int(scope.query('*esr?'))
    print('event status register: 0b{:08b}'.format(r))
    r = scope.query('allev?').strip()
    print('all event messages: {}'.format(r))
    # Calculate waveform
    unscaled_wave = np.array(bin_wave, dtype=np.uint8)
    unscaled_wave = np.reshape(unscaled_wave, (record, 2))
    unscaled_wave_l = unscaled_wave[: , 0]
    unscaled_wave_h = unscaled_wave[: , 1]
    unscaled_wave = unscaled_wave_h * 256 + unscaled_wave_l;
    unscaled_wave = np.array(unscaled_wave, dtype=np.int16)    
    scaled_wave = (unscaled_wave - vpos) * vscale + voff
    return scaled_wave
    
def vertical_scale_autoset(vgs_ena, vds_ena, id_ena, vgs_chn, vds_chn, id_chn, vertical_margin_ratio_h, vertical_margin_ratio_l, vertical_autoset_ratio):
    vgs_autoset_stage = 0
    vds_autoset_stage = 0
    id_autoset_stage = 0
    scope.write('MEASUrement:DELETEALL')
    # Read the waveform data
    while (vgs_autoset_stage < 3 or vds_autoset_stage < 3 or id_autoset_stage < 3):
        if vgs_ena > 0:
            vgs_chn_str = 'CH' + str(vgs_chn)
            if vgs_autoset_stage == 0: 
                # Set up the measurement parameters
                scope.write('MEASUrement:MEAS101:TYPE Maximum')
                # Set up the measurement source
                scope.write('MEASUrement:MEAS101:SOURCE ' + vgs_chn_str)
                # Set up the measurement parameters
                scope.write('MEASUrement:MEAS102:TYPE Minimum')
                # Set up the measurement source
                scope.write('MEASUrement:MEAS102:SOURCE ' + vgs_chn_str)
                time.sleep(2)
            elif vgs_autoset_stage == 1: 
                # Get vertical resolution
                # scope.write('data:source ' + vgs_chn_str)
                # vgs_off = float(scope.query('wfmoutpre:yzero?')) # reference voltage
                # vgs_pos = float(scope.query('wfmoutpre:yoff?')) # reference position (level)
                vgs_off = float(scope.query(vgs_chn_str + ':OFFSET?')) # # reference offset
                vgs_pos = float(scope.query(vgs_chn_str + ':POSition?')) # reference position (level)
                vgs_scale = float(scope.query(vgs_chn_str + ':SCAle?'))
                vgs_chn_max = (5 - vgs_pos) * vgs_scale + vgs_off
                vgs_chn_min = (5 + vgs_pos) * -vgs_scale + vgs_off
                vgs_chn_pp = 10 * vgs_scale
                vgs_margin_limit = vgs_chn_pp * (1 - vertical_margin_ratio_h)
                vgs_max = float(scope.query('MEASUrement:MEAS101:RESUlts:CURRentacq:MEAN?'))
                vgs_min = float(scope.query('MEASUrement:MEAS102:RESUlts:CURRentacq:MEAN?'))
                if vgs_max > 1e10 or vgs_max < -1e10 or vgs_min > 1e10 or vgs_min < -1e10:
                    # Clip deceted
                    vgs_scale = vgs_scale * 2
                    scope.write(vgs_chn_str + ':SCAle ' + str(vgs_scale))
                elif vgs_max  > (vgs_chn_max - vgs_margin_limit) or vgs_min < vgs_chn_min + vgs_margin_limit:
                    vgs_scale = vgs_scale / vertical_autoset_ratio;
                    scope.write(vgs_chn_str + ':SCAle ' + str(vgs_scale))
                else:
                    vgs_off_calc = (vgs_max + vgs_min) / 2
                    scope.write(vgs_chn_str + ':OFFSET ' + str(vgs_off_calc))
                    vgs_pos_calc = 0
                    scope.write(vgs_chn_str + ':POSition ' + str(vgs_pos_calc))
                    vgs_scale = (vgs_max - vgs_min) / 10 / ((vertical_margin_ratio_h + vertical_margin_ratio_l) / 2)
                    scope.write(vgs_chn_str + ':SCAle ' + str(vgs_scale))
                    vgs_autoset_stage = 2
            elif vgs_autoset_stage == 2: 
                # Fine tuning
                # Get vertical resolution
                # scope.write('data:source ' + vgs_chn_str)
                # vgs_off = float(scope.query('wfmoutpre:yzero?')) # reference voltage
                # vgs_pos = float(scope.query('wfmoutpre:yoff?')) # reference position (level)
                vgs_off = float(scope.query(vgs_chn_str + ':OFFSET?')) # # reference offset
                vgs_pos = float(scope.query(vgs_chn_str + ':POSition?')) # reference position (level)
                vgs_scale = float(scope.query(vgs_chn_str + ':SCAle?'))
                vgs_chn_max = (5 - vgs_pos) * vgs_scale + vgs_off
                vgs_chn_min = (5 + vgs_pos) * -vgs_scale + vgs_off
                vgs_chn_pp = 10 * vgs_scale
                vgs_margin_high_h = vgs_chn_min + vgs_chn_pp * vertical_margin_ratio_h
                vgs_margin_high_l = vgs_chn_min + vgs_chn_pp * vertical_margin_ratio_l
                vgs_margin_low_h = vgs_chn_min + vgs_chn_pp * (1 - vertical_margin_ratio_l)
                vgs_margin_low_l = vgs_chn_min + vgs_chn_pp * (1 - vertical_margin_ratio_h)
                vgs_margin_limit = vgs_chn_pp * (1 - vertical_margin_ratio_h)
                vgs_max = float(scope.query('MEASUrement:MEAS101:RESUlts:CURRentacq:MEAN?'))
                vgs_min = float(scope.query('MEASUrement:MEAS102:RESUlts:CURRentacq:MEAN?'))
                if vgs_max > 1e10 or vgs_max < -1e10 or vgs_min > 1e10 or vgs_min < -1e10:
                    # Clip deceted
                    vgs_scale = vgs_scale * 2
                    scope.write(vgs_chn_str + ':SCAle ' + str(vgs_scale))
                elif vgs_max > vgs_margin_high_h or vgs_max  < vgs_margin_high_l or vgs_min > vgs_margin_low_h or vgs_min < vgs_margin_low_l:
                    vgs_off_calc = (vgs_max + vgs_min) / 2
                    scope.write(vgs_chn_str + ':OFFSET ' + str(vgs_off_calc))
                    vgs_pos_calc = 0
                    scope.write(vgs_chn_str + ':POSition ' + str(vgs_pos_calc))
                    vgs_scale = (vgs_max - vgs_min) / 10 / (1 - (1 - (vertical_margin_ratio_h + vertical_margin_ratio_l) / 2) * 2)
                    scope.write(vgs_chn_str + ':SCAle ' + str(vgs_scale))
                else:
                    # Delete specified measurement
                    scope.write('MEASUrement:DELete ' + '\"' + 'MEAS101' + '\"')
                    scope.write('MEASUrement:DELete ' + '\"' + 'MEAS102' + '\"')
                    vgs_autoset_stage = 3
            else:
                vgs_autoset_stage = 3
        if vds_ena > 0:
            vds_chn_str = 'CH' + str(vds_chn)
            if vds_autoset_stage == 0: 
                # Set up the measurement parameters
                scope.write('MEASUrement:MEAS103:TYPE Maximum')
                # Set up the measurement source
                scope.write('MEASUrement:MEAS103:SOURCE ' + vds_chn_str)
                # Set up the measurement parameters
                scope.write('MEASUrement:MEAS104:TYPE Minimum')
                # Set up the measurement source
                scope.write('MEASUrement:MEAS104:SOURCE ' + vds_chn_str)
                time.sleep(2)
            elif vds_autoset_stage == 1: 
                # Get vertical resolution
                # scope.write('data:source ' + vds_chn_str)
                # vds_off = float(scope.query('wfmoutpre:yzero?')) # reference voltage
                # vds_pos = float(scope.query('wfmoutpre:yoff?')) # reference position (level)
                vds_off = float(scope.query(vds_chn_str + ':OFFSET?')) # # reference offset
                vds_pos = float(scope.query(vds_chn_str + ':POSition?')) # reference position (level)
                vds_scale = float(scope.query(vds_chn_str + ':SCAle?'))
                vds_chn_max = (5 - vds_pos) * vds_scale + vds_off
                vds_chn_min = (5 + vds_pos) * -vds_scale + vds_off
                vds_chn_pp = 10 * vds_scale
                vds_margin_limit = vds_chn_pp * (1 - vertical_margin_ratio_h)
                vds_max = float(scope.query('MEASUrement:MEAS103:RESUlts:CURRentacq:MEAN?'))
                vds_min = float(scope.query('MEASUrement:MEAS104:RESUlts:CURRentacq:MEAN?'))
                if vds_max > 1e10 or vds_max < -1e10 or vds_min > 1e10 or vds_min < -1e10:
                    # Clip deceted
                    vds_scale = vds_scale * 2
                    scope.write(vds_chn_str + ':SCAle ' + str(vds_scale))
                elif vds_max  > (vds_chn_max - vds_margin_limit) or vds_min < vds_chn_min + vds_margin_limit:
                    vds_scale = vds_scale / vertical_autoset_ratio;
                    scope.write(vds_chn_str + ':SCAle ' + str(vds_scale))
                else:
                    vds_off_calc = (vds_max + vds_min) / 2
                    scope.write(vds_chn_str + ':OFFSET ' + str(vds_off_calc))
                    vds_pos_calc = 0
                    scope.write(vds_chn_str + ':POSition ' + str(vds_pos_calc))
                    vds_scale = (vds_max - vds_min) / 10 / ((vertical_margin_ratio_h + vertical_margin_ratio_l) / 2)
                    scope.write(vds_chn_str + ':SCAle ' + str(vds_scale))
                    vds_autoset_stage = 2
            elif vds_autoset_stage == 2: 
                # Fine tuning
                # Get vertical resolution
                # scope.write('data:source ' + vds_chn_str)
                # vds_off = float(scope.query('wfmoutpre:yzero?')) # reference voltage
                # vds_pos = float(scope.query('wfmoutpre:yoff?')) # reference position (level)
                vds_off = float(scope.query(vds_chn_str + ':OFFSET?')) # # reference offset
                vds_pos = float(scope.query(vds_chn_str + ':POSition?')) # reference position (level)
                vds_scale = float(scope.query(vds_chn_str + ':SCAle?'))
                vds_chn_max = (5 - vds_pos) * vds_scale + vds_off
                vds_chn_min = (5 + vds_pos) * -vds_scale + vds_off
                vds_chn_pp = 10 * vds_scale
                vds_margin_high_h = vds_chn_min + vds_chn_pp * vertical_margin_ratio_h
                vds_margin_high_l = vds_chn_min + vds_chn_pp * vertical_margin_ratio_l
                vds_margin_low_h = vds_chn_min + vds_chn_pp * (1 - vertical_margin_ratio_l)
                vds_margin_low_l = vds_chn_min + vds_chn_pp * (1 - vertical_margin_ratio_h)
                vds_margin_limit = vds_chn_pp * (1 - vertical_margin_ratio_h)
                vds_max = float(scope.query('MEASUrement:MEAS103:RESUlts:CURRentacq:MEAN?'))
                vds_min = float(scope.query('MEASUrement:MEAS104:RESUlts:CURRentacq:MEAN?'))
                if vds_max > 1e10 or vds_max < -1e10 or vds_min > 1e10 or vds_min < -1e10:
                    # Clip deceted
                    vds_scale = vds_scale * 2
                    scope.write(vds_chn_str + ':SCAle ' + str(vds_scale))
                elif vds_max > vds_margin_high_h or vds_max  < vds_margin_high_l or vds_min > vds_margin_low_h or vds_min < vds_margin_low_l:
                    vds_off_calc = (vds_max + vds_min) / 2
                    scope.write(vds_chn_str + ':OFFSET ' + str(vds_off_calc))
                    vds_pos_calc = 0
                    scope.write(vds_chn_str + ':POSition ' + str(vds_pos_calc))
                    vds_scale = (vds_max - vds_min) / 10 / (1 - (1 - (vertical_margin_ratio_h + vertical_margin_ratio_l) / 2) * 2)
                    scope.write(vds_chn_str + ':SCAle ' + str(vds_scale))
                else:
                    # Delete specified measurement
                    scope.write('MEASUrement:DELete ' + '\"' + 'MEAS103' + '\"')
                    scope.write('MEASUrement:DELete ' + '\"' + 'MEAS104' + '\"')
                    vds_autoset_stage = 3
            else:
                vds_autoset_stage = 3
        else:
            vds_autoset_stage = 3
        if id_ena > 0:
            id_chn_str = 'CH' + str(id_chn)
            if id_autoset_stage == 0: 
                # Set up the measurement parameters
                scope.write('MEASUrement:MEAS105:TYPE Maximum')
                # Set up the measurement source
                scope.write('MEASUrement:MEAS105:SOURCE ' + id_chn_str)
                # Set up the measurement parameters
                scope.write('MEASUrement:MEAS106:TYPE Minimum')
                # Set up the measurement source
                scope.write('MEASUrement:MEAS106:SOURCE ' + id_chn_str)
                time.sleep(2)
            elif id_autoset_stage == 1: 
                # Get vertical resolution
                # scope.write('data:source ' + id_chn_str)
                # id_off = float(scope.query('wfmoutpre:yzero?')) # reference voltage
                # id_pos = float(scope.query('wfmoutpre:yoff?')) # reference position (level)
                id_off = float(scope.query(id_chn_str + ':OFFSET?')) # # reference offset
                id_pos = float(scope.query(id_chn_str + ':POSition?')) # reference position (level)
                id_scale = float(scope.query(id_chn_str + ':SCAle?'))
                id_chn_max = (5 - id_pos) * id_scale + id_off
                id_chn_min = (5 + id_pos) * -id_scale + id_off
                id_chn_pp = 10 * id_scale
                id_margin_limit = id_chn_pp * (1 - vertical_margin_ratio_h)
                id_max = float(scope.query('MEASUrement:MEAS105:RESUlts:CURRentacq:MEAN?'))
                id_min = float(scope.query('MEASUrement:MEAS106:RESUlts:CURRentacq:MEAN?'))
                if id_max > 1e10 or id_max < -1e10 or id_min > 1e10 or id_min < -1e10:
                    # Clip deceted
                    id_scale = id_scale * 2
                    scope.write(id_chn_str + ':SCAle ' + str(id_scale))
                elif id_max  > (id_chn_max - id_margin_limit) or id_min < id_chn_min + id_margin_limit:
                    id_scale = id_scale / vertical_autoset_ratio;
                    scope.write(id_chn_str + ':SCAle ' + str(id_scale))
                else:
                    id_off_calc = (id_max + id_min) / 2
                    scope.write(id_chn_str + ':OFFSET ' + str(id_off_calc))
                    id_pos_calc = 0
                    scope.write(id_chn_str + ':POSition ' + str(id_pos_calc))
                    id_scale = (id_max - id_min) / 10 / ((vertical_margin_ratio_h + vertical_margin_ratio_l) / 2)
                    scope.write(id_chn_str + ':SCAle ' + str(id_scale))
                    id_autoset_stage = 2
            elif id_autoset_stage == 2: 
                # Fine tuning
                # Get vertical resolution
                # scope.write('data:source ' + id_chn_str)
                # id_off = float(scope.query('wfmoutpre:yzero?')) # reference voltage
                # id_pos = float(scope.query('wfmoutpre:yoff?')) # reference position (level)
                id_off = float(scope.query(id_chn_str + ':OFFSET?')) # # reference offset
                id_pos = float(scope.query(id_chn_str + ':POSition?')) # reference position (level)
                id_scale = float(scope.query(id_chn_str + ':SCAle?'))
                id_chn_max = (5 - id_pos) * id_scale + id_off
                id_chn_min = (5 + id_pos) * -id_scale + id_off
                id_chn_pp = 10 * id_scale
                id_margin_high_h = id_chn_min + id_chn_pp * vertical_margin_ratio_h
                id_margin_high_l = id_chn_min + id_chn_pp * vertical_margin_ratio_l
                id_margin_low_h = id_chn_min + id_chn_pp * (1 - vertical_margin_ratio_l)
                id_margin_low_l = id_chn_min + id_chn_pp * (1 - vertical_margin_ratio_h)
                id_margin_limit = id_chn_pp * (1 - vertical_margin_ratio_h)
                id_max = float(scope.query('MEASUrement:MEAS105:RESUlts:CURRentacq:MEAN?'))
                print('id_max ' + str(id_max))
                id_min = float(scope.query('MEASUrement:MEAS106:RESUlts:CURRentacq:MEAN?'))
                print('id_min ' + str(id_min))
                if id_max > 1e10 or id_max < -1e10 or id_min > 1e10 or id_min < -1e10:
                    # Clip deceted
                    id_scale = id_scale * 2
                    scope.write(id_chn_str + ':SCAle ' + str(id_scale))
                elif id_max > id_margin_high_h or id_max  < id_margin_high_l or id_min > id_margin_low_h or id_min < id_margin_low_l:
                    id_off_calc = (id_max + id_min) / 2
                    scope.write(id_chn_str + ':OFFSET ' + str(id_off_calc))
                    print('id_off_calc ' + str(id_off_calc))
                    id_pos_calc = 0
                    scope.write(id_chn_str + ':POSition ' + str(id_pos_calc))
                    id_scale = (id_max - id_min) / 10 / (1 - (1 - (vertical_margin_ratio_h + vertical_margin_ratio_l) / 2) * 2)
                    scope.write(id_chn_str + ':SCAle ' + str(id_scale))
                else:
                    # Delete specified measurement
                    scope.write('MEASUrement:DELete ' + '\"' + 'MEAS105' + '\"')
                    scope.write('MEASUrement:DELete ' + '\"' + 'MEAS106' + '\"')
                    id_autoset_stage = 3
            else:
                id_autoset_stage = 3
        else:
            id_autoset_stage = 3
        
        
        if ((vgs_autoset_stage == 0) & (vgs_ena == 1)) | \
           ((vds_autoset_stage == 0) & (vds_ena == 1)) | \
           ((id_autoset_stage  == 0) & (id_ena  == 1)) :
            scope.write('MEASUrement:ADDNew \"MEAS1\"')
            scope.write('MEASUrement:MEAS1:TYPe WBGEON')
            # Initialize the AFG configuration
            # Make sure use the last measurement item number to create the trigger
            # In this demo, the last measurement one is number 1, so MEAS1 will be used
            # Becasue in V2.4.4, the 'WBGGSTIM' couldn't specify the measurement number
            print('AFG initialization...')
            scope.write('MEASUrement:MEAS1:WBG:AFGaddress \"' + afg_ip + '\"')
            r = scope.query('MEASUrement:MEAS1:WBG:AFGaddress?')
            print('AFG IP address: ' + r)
            # Test the AFG connection
            scope.write('MEASUrement:MEAS1:WBG:AFGSetup CONNECT')
            # Sets the generator type for WBG measurements
            scope.write('MEASUrement:MEAS1:WBG:GTYPe AFG31000')
            # Set AFG output high level
            scope.write('MEASUrement:MEAS1:WBG:HIGH ' + str(afg_output_h))
            # Set AFG output low level
            scope.write('MEASUrement:MEAS1:WBG:LOW ' + str(afg_output_l))
            # Set AFG output load type to high-z
            scope.write('MEASUrement:MEAS1:WBG:LOAD HIGHZ')
            # Set AFG output pulses number to 2
            scope.write('MEASUrement:MEAS1:WBG:NPULs 2')
            # Set AFG output pulse width for the 1st pulse
            scope.write('MEASUrement:MEAS1:WBG:PW1Val ' + str(pulse_1_width))
            # Set AFG output gap1 after the 1st pulse
            scope.write('MEASUrement:MEAS1:WBG:PG1Val ' + str(pulse_1_gap))
            # Set AFG output gap2 after the 2nd pulse
            scope.write('MEASUrement:MEAS1:WBG:PW2Val ' + str(pulse_2_width))
            # Set AFG output gap2 after the 2nd pulse
            scope.write('MEASUrement:MEAS1:WBG:PG2Val ' + str(pulse_2_gap))
            # Setup configuration on connected AFG
            scope.write('MEASUrement:MEAS1:WBG:AFGSetup RUN')
            time.sleep(5)
            if vgs_ena == 1:
                vgs_autoset_stage = 1
            if vds_ena == 1:
                vds_autoset_stage = 1
            if id_ena == 1:
                id_autoset_stage = 1
        
        # Start acquistions
        scope.write('ACQuire:STATE ON')
        print('Acquisition start')
        time.sleep(1)
        # Start measurement
        # Generate a trigger event
        scope.write('MEASUrement:AUTOset WBGGSTIM')
        # scope.write('AFG:BURSt:TRIGger')
        print('AFG triggered')
        
        # Wait until the acquistion is finished
        busy_flag = 1
        while busy_flag != 0:
            busy_flag = wait_for_scope_acq_stop_or_timeout(acq_wait_timeout_time)
            if busy_flag != 0:
                # Generate a trigger event
                scope.write('MEASUrement:AUTOset WBGGSTIM')
                print('AFG re-triggered')
        

# ----------------------------------------------------

t_start = time.perf_counter()

rm = visa.ResourceManager()
# Create scope object
scope = rm.open_resource(visa_address_scope)
scope.timeout = 30000 # ms
scope.encoding = 'latin_1'
scope.read_termination = '\n'
scope.write_termination = None

vgs_chn_str = 'CH' + str(vgs_chn)
vds_chn_str = 'CH' + str(vds_chn)
id_chn_str  = 'CH' + str(id_chn)

# ----------------------------------------------------
# set up scope
# Default Setup
if rst_scope_ena:
    scope.write('*rst')
    t1 = time.perf_counter()
    # Wait until the scope become free
    wait_for_scope_free()
    t2 = time.perf_counter()
    print('Reset time: {}'.format(t2 - t1))

scope.write('*cls') # clear ESR
r = scope.query('*idn?')
print(r)

# Disable Channel 1
scope.write('DISplay:GLObal:' + 'CH1' + ':STATE ' + 'OFF')
# Eable target Channel
scope.write('DISplay:GLObal:' + vgs_chn_str + ':STATE ' + 'ON')
# Eable target Channel
scope.write('DISplay:GLObal:' + vds_chn_str + ':STATE ' + 'ON')
# Eable target Channel
if vgs_chn_invert != 0:
    scope.write(vgs_chn_str + ':INVert ' + 'ON')
if vds_chn_invert != 0:
    scope.write(vds_chn_str + ':INVert ' + 'ON')
if id_chn_invert != 0:
    scope.write(id_chn_str + ':INVert ' + 'ON')
# Enable alternate unit for current
if id_alt_unit_ratio != 0:
    scope.write(id_chn_str + ':PROBEFunc:EXTUnits:STATE ' + 'ON')
# Set the alternate unit ratio (unit: A/V)
if id_alt_unit_ratio != 0:
    scope.write(id_chn_str + ':SCALERATio ' + str(id_alt_unit_ratio))
# Invert Id or not
scope.write('DISplay:GLObal:' + id_chn_str + ':STATE ' + 'ON')
# Query target Channel display status
r = scope.query('DISplay:GLObal:' + vgs_chn_str + ':STATE?')
print(vgs_chn_str + ' dispaly status: ' + r)

# Deskew of probes/channels (unit: second, -125ns to +125ns with 40ps resolution)
scope.write(vgs_chn_str + ':DESKew ' + str(vgs_chn_deskew_sec))
scope.write(vds_chn_str + ':DESKew ' + str(vds_chn_deskew_sec))
scope.write(id_chn_str + ':DESKew ' + str(id_chn_deskew_sec))

# Set High Resolution mode
scope.write('ACQuire:MODe HIRes')
# Query scope acquistion mode
r = scope.query('ACQuire:MODe?')
print('Acquisition mode: ' + r)

# Set horizontal settings
# Set herizontal mode to manual
scope.write('HORizontal:MODE MANual')
# Query herizontal mode
r = scope.query('HORizontal:MODE?')
print('Herizontal mode: ' + r)

# Set herizontal sample rate
if sample_rate <= 0:
    sample_rate = 12.5e9
scope.write('HORizontal:MODE:SAMPLERate ' + str(sample_rate))
# Query herizontal mode
r = scope.query('HORizontal:MODE:SAMPLERate?')
print('Herizontal sample rate: ' + r)

# Calculate sample rate from pulse width
if recond_length <= 0:
    pulses_width = pulse_1_width + pulse_1_gap + pulse_2_width + pulse_2_gap
    recond_length = int(pulses_width * 2 * sample_rate)
# Set herizontal record length
scope.write('HORizontal:MODE:RECOrdlength ' + str(recond_length))
# Query herizontal mode
r = scope.query('HORizontal:MODE:RECOrdlength?')
print('Herizontal record length: ' + r)

# Set trigger location
if horizontal_position <= 0:
    horizontal_position = 25
# Set herizontal record length
scope.write('HORIZONTAL:POSITION ' + str(horizontal_position))
# Query herizontal mode
r = scope.query('HORIZONTAL:POSITION?')
print('Herizontal position: ' + r)

# Set Trigger type to edge
scope.write('TRIGger:A:EDGE:COUPling NOISErej')
# Query Trigger type
r = scope.query('TRIGger:A:EDGE:COUPling?')
print('Trigger type: ' + r)

# Set Trigger source
scope.write('TRIGger:A:EDGE:SOUrce ' + vgs_chn_str)
# Query Trigger source
r = scope.query('TRIGger:A:EDGE:SOUrce?')
print('Trigger source: ' + r)

# Set Trigger level
if trig_lvl == 0:
    trig_lvl = vgs_amplitude / 2;
scope.write('TRIGGER:A:LEVEL:' + vgs_chn_str + ' ' + str(trig_lvl))
# Query Trigger level
r = scope.query('TRIGGER:A:LEVEL:' + vgs_chn_str + '?')
print('Trigger level: ' + r)

# Set Trigger mode to AUTO/NORMal
scope.write('TRIGger:A:MODe NORMal')
# Query Trigger mode
r = scope.query('TRIGger:A:MODe?')
print('Trigger mode: ' + r)

# Single trigger
scope.write('acquire:stopafter SEQuence')
r = scope.query('ACQuire:STATE?') 
print('Acquisition mode: ' + r)

# Start acquistions
scope.write('ACQuire:STATE ON')
print('Acquisition start')

# Init the vertical scales
if autoset_vertical_ena:
    if autoset_vgs_ena:
        vgs_scale = vgs_amplitude / 5
        scope.write(vgs_chn_str + ':SCAle ' + str(vgs_scale))
    else:
        scope.write(vgs_chn_str + ':SCAle ' + str(vgs_scale_manual))
        scope.write(vgs_chn_str + ':OFFSET ' + str(vgs_offset_manual))
        scope.write(vgs_chn_str + ':POSition ' + str(vgs_position_manual))
    if autoset_vds_ena:
        vds_scale = vds_amplitude / 5
        scope.write(vds_chn_str + ':SCAle ' + str(vds_scale))
    else:
        scope.write(vds_chn_str + ':SCAle ' + str(vds_scale_manual))
        scope.write(vds_chn_str + ':OFFSET ' + str(vds_offset_manual))
        scope.write(vds_chn_str + ':POSition ' + str(vds_position_manual))
    if autoset_id_ena:
        id_scale  = id_amplitude  / 5
        scope.write(id_chn_str + ':SCAle ' + str(id_scale))
    else:
        scope.write(id_chn_str + ':SCAle ' + str(id_scale_manual))
        scope.write(id_chn_str + ':OFFSET ' + str(id_offset_manual))
        scope.write(id_chn_str + ':POSition ' + str(id_position_manual))
    vertical_scale_autoset(autoset_vgs_ena, autoset_vds_ena, autoset_id_ena, vgs_chn, vds_chn, id_chn, vertical_margin_ratio_h, vertical_margin_ratio_l, vertical_autoset_ratio)
else:
    scope.write(vgs_chn_str + ':SCAle ' + str(vgs_scale_manual))
    scope.write(vds_chn_str + ':SCAle ' + str(vds_scale_manual))
    scope.write(id_chn_str + ':SCAle ' + str(id_scale_manual))
    scope.write(vgs_chn_str + ':OFFSET ' + str(vgs_offset_manual))
    scope.write(vds_chn_str + ':OFFSET ' + str(vds_offset_manual))
    scope.write(id_chn_str + ':OFFSET ' + str(id_offset_manual))
    scope.write(vgs_chn_str + ':POSition ' + str(vgs_position_manual))
    scope.write(vds_chn_str + ':POSition ' + str(vds_position_manual))
    scope.write(id_chn_str + ':POSition ' + str(id_position_manual))
print('Vertical settings adjust complete')
# ----------------------------------------------------

# Stop acquistions
scope.write('ACQuire:STATE OFF')
print('Acquisition stopped')

# Set the WBG-DPT test items
# ====================================================
# Setup measurements
scope.write('MEASUrement:DELETEALL')
# Add measurements
if id_math_chn > 0:
    scope.write('MEASUrement:ADDNew \"MEAS100\"')
    scope.write('MEASUrement:MEAS100:TYPe MEAN')
    scope.write('MEASUrement:MEAS100:SOUrce1 ' + id_chn_str)
    scope.write('MEASUrement:MEAS100:GATing:GLOBal OFF')
    scope.write('MEASUrement:MEAS100:GATing TIME')
    herizontal_time_beg = 0 - int(horizontal_position * recond_length / 100) / sample_rate
    id_gate_time_beg = int(id_zero_gate_beg * recond_length) / sample_rate + herizontal_time_beg
    id_gate_time_end = int(id_zero_gate_end * recond_length) / sample_rate + herizontal_time_beg
    scope.write('MEASUrement:MEAS100:GATing:STARTtime ' + str(id_gate_time_beg))
    scope.write('MEASUrement:MEAS100:GATing:ENDtime ' + str(id_gate_time_end))
    id_mea_str = 'MATH' + str(id_chn)
else:
    id_mea_str = id_chn_str

# Create all test items in the measurement list
scope.write('MEASUrement:ADDNew \"MEAS1\"')
scope.write('MEASUrement:MEAS1:TYPe WBGEON')
scope.write('MEASUrement:ADDNew \"MEAS2\"')
scope.write('MEASUrement:MEAS2:TYPe WBGEOFF')
scope.write('MEASUrement:ADDNew \"MEAS3\"')
scope.write('MEASUrement:MEAS3:TYPe WBGVPEAK')
scope.write('MEASUrement:ADDNew \"MEAS4\"')
scope.write('MEASUrement:MEAS4:TYPe WBGIPEAK')
scope.write('MEASUrement:ADDNew \"MEAS5\"')
scope.write('MEASUrement:MEAS5:TYPe WBGTDON')
scope.write('MEASUrement:ADDNew \"MEAS6\"')
scope.write('MEASUrement:MEAS6:TYPe WBGTDOFF')
scope.write('MEASUrement:ADDNew \"MEAS7\"')
scope.write('MEASUrement:MEAS7:TYPe WBGTR')
scope.write('MEASUrement:ADDNew \"MEAS8\"')
scope.write('MEASUrement:MEAS8:TYPe WBGTF')
scope.write('MEASUrement:ADDNew \"MEAS9\"')
scope.write('MEASUrement:MEAS9:TYPe WBGTON')
scope.write('MEASUrement:ADDNew \"MEAS10\"')
scope.write('MEASUrement:MEAS10:TYPe WBGTOFF')
scope.write('MEASUrement:ADDNew \"MEAS11\"')
scope.write('MEASUrement:MEAS11:TYPe WBGDDT')

# Set DUT type to MOSFET
scope.write('MEASUrement:WBG:PDEVice MOSFET')

# Set measurements signal sources
scope.write('MEASUrement:MEAS1:SOUrce1 ' + vds_chn_str)
scope.write('MEASUrement:MEAS1:SOUrce2 ' + id_mea_str)
scope.write('MEASUrement:MEAS1:SOUrce3 ' + vgs_chn_str)

scope.write('MEASUrement:MEAS2:SOUrce1 ' + vds_chn_str)
scope.write('MEASUrement:MEAS2:SOUrce2 ' + id_mea_str)
scope.write('MEASUrement:MEAS2:SOUrce3 ' + vgs_chn_str)

scope.write('MEASUrement:MEAS3:SOUrce1 ' + vds_chn_str)
scope.write('MEASUrement:MEAS3:SOUrce2 ' + id_mea_str)
scope.write('MEASUrement:MEAS3:SOUrce3 ' + vgs_chn_str)

scope.write('MEASUrement:MEAS4:SOUrce1 ' + vds_chn_str)
scope.write('MEASUrement:MEAS4:SOUrce2 ' + id_mea_str)
scope.write('MEASUrement:MEAS4:SOUrce3 ' + vgs_chn_str)

scope.write('MEASUrement:MEAS5:SOUrce1 ' + vds_chn_str)
scope.write('MEASUrement:MEAS5:SOUrce2 ' + id_mea_str)
scope.write('MEASUrement:MEAS5:SOUrce3 ' + vgs_chn_str)

scope.write('MEASUrement:MEAS6:SOUrce1 ' + vds_chn_str)
scope.write('MEASUrement:MEAS6:SOUrce2 ' + id_mea_str)
scope.write('MEASUrement:MEAS6:SOUrce3 ' + vgs_chn_str)

scope.write('MEASUrement:MEAS7:SOUrce1 ' + vds_chn_str)
scope.write('MEASUrement:MEAS7:SOUrce2 ' + id_mea_str)
scope.write('MEASUrement:MEAS7:SOUrce3 ' + vgs_chn_str)

scope.write('MEASUrement:MEAS8:SOUrce1 ' + vds_chn_str)
scope.write('MEASUrement:MEAS8:SOUrce2 ' + id_mea_str)
scope.write('MEASUrement:MEAS8:SOUrce3 ' + vgs_chn_str)

scope.write('MEASUrement:MEAS9:SOUrce1 ' + vds_chn_str)
scope.write('MEASUrement:MEAS9:SOUrce2 ' + id_mea_str)
scope.write('MEASUrement:MEAS9:SOUrce3 ' + vgs_chn_str)

scope.write('MEASUrement:MEAS10:SOUrce1 ' + vds_chn_str)
scope.write('MEASUrement:MEAS10:SOUrce2 ' + id_mea_str)
scope.write('MEASUrement:MEAS10:SOUrce3 ' + vgs_chn_str)

scope.write('MEASUrement:MEAS11:SOUrce1 ' + id_mea_str)
scope.write('MEASUrement:MEAS11:SOUrce2 ' + vgs_chn_str)

# ====================================================

e_on_list = []
e_off_list = []
v_peak_list = []
i_peak_list = []
td_on_list = []
td_off_list = []
t_r_list = []
t_f_list = []
t_on_list = []
t_off_list = []

if local_table_save_ena != 0:
    with open(path_local + result_local_name, mode="wt") as f:
        f.write('e_on,e_off,v_peak,i_peak,td_on,td_off,t_r,t_f,t_on,t_off\n')

# Sometimes the 1st trigger didn't work, so do it once in beginning
# Wait until the scope become free
wait_for_scope_free()

# Initialize the AFG configuration
# Make sure use the last measurement item number to create the trigger
# In this demo, the last measurement one is number 11, so MEAS11 will be used
# Becasue in V2.4.4, the 'WBGGSTIM' couldn't specify the measurement number
print('AFG initialization...')
scope.write('MEASUrement:MEAS11:WBG:AFGaddress \"' + afg_ip + '\"')
r = scope.query('MEASUrement:MEAS11:WBG:AFGaddress?')
print('AFG IP address: ' + r)
# Test the AFG connection
scope.write('MEASUrement:MEAS11:WBG:AFGSetup CONNECT')
# Sets the generator type for WBG measurements
scope.write('MEASUrement:MEAS11:WBG:GTYPe AFG31000')
# Set AFG output high level
scope.write('MEASUrement:MEAS11:WBG:HIGH ' + str(afg_output_h))
# Set AFG output low level
scope.write('MEASUrement:MEAS11:WBG:LOW ' + str(afg_output_l))
# Set AFG output load type to high-z
scope.write('MEASUrement:MEAS11:WBG:LOAD HIGHZ')
# Set AFG output pulses number to 2
scope.write('MEASUrement:MEAS11:WBG:NPULs 2')
# Set AFG output pulse width for the 1st pulse
scope.write('MEASUrement:MEAS11:WBG:PW1Val ' + str(pulse_1_width))
# Set AFG output gap1 after the 1st pulse
scope.write('MEASUrement:MEAS11:WBG:PG1Val ' + str(pulse_1_gap))
# Set AFG output gap2 after the 2nd pulse
scope.write('MEASUrement:MEAS11:WBG:PW2Val ' + str(pulse_2_width))
# Set AFG output gap2 after the 2nd pulse
scope.write('MEASUrement:MEAS11:WBG:PG2Val ' + str(pulse_2_gap))
# Setup configuration on connected AFG
scope.write('MEASUrement:MEAS11:WBG:AFGSetup RUN')

    
for test_cnt in range(test_iter_num):

    # Test iteration
    print('Test iteration No.', str(test_cnt + 1))
    # Start acquistions
    scope.write('ACQuire:STATE ON')
    print('Acquisition start')
    time.sleep(1)
    # Start measurement
    # Generate a trigger event
    scope.write('MEASUrement:AUTOset WBGGSTIM')
    # scope.write('AFG:BURSt:TRIGger')
    print('AFG triggered')
    
    # Wait until the acquistion is finished
    busy_flag = 1
    while busy_flag != 0:
        busy_flag = wait_for_scope_acq_stop_or_timeout(acq_wait_timeout_time)
        if busy_flag != 0:
            # Generate a trigger event
            scope.write('MEASUrement:AUTOset WBGGSTIM')
            print('AFG re-triggered')
        
    if id_math_chn > 0:
        id_offset_str = scope.query('MEASUrement:MEAS100:SUBGROUP:RESUlts:CURRentacq:MEAN? \"INPUT\"')
        print('Id offset measured: ' + id_offset_str + ' A')
        id_offset = float(id_offset_str)
        scope.write('MATH:' + id_mea_str + ':DEFine \"' + id_chn_str + '-' + str(id_offset) + '\"')
        # Wait until the data are updated due to the math change
        time.sleep(2)
        
    # Read the result
    e_on = float(scope.query('MEASUrement:MEAS1:SUBGROUP:RESUlts:CURRentacq:MEAN? "EON"'))
    e_off = float(scope.query('MEASUrement:MEAS2:SUBGROUP:RESUlts:CURRentacq:MEAN? "EOFF"'))
    v_peak = float(scope.query('MEASUrement:MEAS3:SUBGROUP:RESUlts:CURRentacq:MEAN? "VPEAK"'))
    i_peak = float(scope.query('MEASUrement:MEAS4:SUBGROUP:RESUlts:CURRentacq:MEAN? "IPEAK"'))
    td_on = float(scope.query('MEASUrement:MEAS5:SUBGROUP:RESUlts:CURRentacq:MEAN? "TDON"'))
    td_off = float(scope.query('MEASUrement:MEAS6:SUBGROUP:RESUlts:CURRentacq:MEAN? "TDOFF"'))
    t_r = float(scope.query('MEASUrement:MEAS7:SUBGROUP:RESUlts:CURRentacq:MEAN? "TR"'))
    t_f = float(scope.query('MEASUrement:MEAS8:SUBGROUP:RESUlts:CURRentacq:MEAN? "TF"'))
    t_on = float(scope.query('MEASUrement:MEAS9:SUBGROUP:RESUlts:CURRentacq:MEAN? "TON"'))
    t_off = float(scope.query('MEASUrement:MEAS10:SUBGROUP:RESUlts:CURRentacq:MEAN? "TOFF"'))
    d_dt = float(scope.query('MEASUrement:MEAS11:SUBGROUP:RESUlts:CURRentacq:MEAN? "DBYDT"'))
    # d_dt = float(scope.query('MEASUrement:MEAS11:RESUlts:CURRentacq:MEAN?'))

    e_on_list.append(str(e_on))
    e_off_list.append(str(e_off))
    v_peak_list.append(str(v_peak))
    i_peak_list.append(str(i_peak))
    td_on_list.append(str(td_on))
    td_off_list.append(str(td_off))
    t_r_list.append(str(t_r))
    t_f_list.append(str(t_f))
    t_on_list.append(str(t_on))
    t_off_list.append(str(t_off))

    print('Test results')
    print('------------------------------')
    print('Eon     :' + e_on_list[test_cnt])
    print('Eoff    :' + e_off_list[test_cnt])
    print('Vpeak   :' + v_peak_list[test_cnt])
    print('Ipeak   :' + i_peak_list[test_cnt])
    print('Td(on)  :' + td_on_list[test_cnt])
    print('Td(off) :' + td_off_list[test_cnt])
    print('Tr      :' + t_r_list[test_cnt])
    print('Tf      :' + t_f_list[test_cnt])
    print('Ton     :' + t_on_list[test_cnt])
    print('Toff    :' + t_off_list[test_cnt])
    print('d/dt    :' + str(d_dt))
    print('------------------------------')
    

    # Save waveforms, table, screen on remote disk (scope)
    if remote_table_save_ena != 0:
        scope.write('SAVe:EVENTtable:MEASUrement ' + '\"' + path_scope + result_table_name + '_' + str(test_cnt) + result_table_ext + '\"')
        print('Save results table on sopce disk')
        r = scope.query('*opc?')
    if remote_screen_save_ena != 0:   
        r = scope.write('SAVe:IMAGe ' + '\"' + path_scope + screen_name + '_' + str(test_cnt) + screen_ext + '\"')
        print('Save screen capture on sopce disk')
        # Wait untill operation is finished
        r = scope.query('*opc?')
    if remote_wfm_save_ena != 0:
        scope.write('SAVe:WAVEform ' + vgs_chn_str + ','+ '\"' + path_scope + 'vgs_' + str(test_cnt) + '.wfm' + '\"')
        print('Save Vgs waveform on sopce disk')
        scope.write('SAVe:WAVEform ' + vds_chn_str + ','+ '\"' + path_scope + 'vds_' + str(test_cnt) + '.wfm' + '\"')
        print('Save Vds waveform on sopce disk')
        scope.write('SAVe:WAVEform ' + id_mea_str + ','+ '\"' + path_scope + 'id_' + str(test_cnt) + '.wfm' + '\"')
        print('Save Id waveform on sopce disk')
        # Wait untill operation is finished
        r = scope.query('*opc?')
    if remote_session_save_ena != 0:
        scope.write('SAVe:SESsion ' + '\"' + path_scope + session_name + '_' + str(test_cnt) + '.tss\"')
        print('Save session file on sopce disk')
        r = scope.query('*opc?')

    # Save waveforms to local disk
    if local_wfm_save_ena != 0:
        # horizontal (time)
        scaled_time = read_wfm_horizontal()
        # Save time axis to file
        np.savetxt(path_local + 'wfm_t_' + str(test_cnt) + '.txt', scaled_time) 
        # Vertical (voltage)
        scaled_wave_vgs = read_wfm_vertical(vgs_chn)
        # Save the vgs waveform to file
        np.savetxt(path_local + 'wfm_Vgs_' + str(test_cnt) + '.txt', scaled_wave_vgs)
        # Vertical (voltage)
        scaled_wave_vds = read_wfm_vertical(vds_chn)
        # Save the vgs waveform to file
        np.savetxt(path_local + 'wfm_Vds_' + str(test_cnt) + '.txt', scaled_wave_vds)
        # Vertical (voltage)
        scaled_wave_id = read_wfm_vertical(id_chn)
        # Save the vgs waveform to file
        np.savetxt(path_local + 'wfm_Id_' + str(test_cnt) + '.txt', scaled_wave_id)
        
    time.sleep(test_iter_intvl)

    if local_table_save_ena != 0:
        with open(path_local + result_local_name, mode="at") as f:
            f.write(\
                e_on_list[test_cnt] + ',' + \
                e_off_list[test_cnt] + ',' + \
                v_peak_list[test_cnt] + ',' + \
                i_peak_list[test_cnt] + ',' + \
                td_on_list[test_cnt] + ',' + \
                td_off_list[test_cnt] + ',' + \
                t_r_list[test_cnt] + ',' + \
                t_f_list[test_cnt] + ',' + \
                t_on_list[test_cnt] + ',' + \
                t_off_list[test_cnt] + ',' + \
                '\n')
      
scope.close()
if 0:
    afg.close()
rm.close()

t_end = time.perf_counter()
print('Executing time: {} seconds'.format(t_end - t_start))



