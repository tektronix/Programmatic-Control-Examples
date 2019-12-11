# Python3 LE320 Two-unit Control
# https://www.tek.com/sample-license

# LE320 WIN32COM module is installed with LE Control Software
# LE Control Software v2.7.0.785 (066-1624-06)
# https://www.tek.com/bit-error-rate-tester/le320-software-0

# LE320 WIN32COM module is 32-bit only; must use 32-bit Python

import logging
import win32com.client # https://pypi.org/project/pywin32/

# constants
le_mode = {'tap9R':1, 'tap9':2, 'tap4':3, 'spm':4, 'cds':5}
chan = 1

# configure logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO) # normal
#logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG) # verbose

# create two handles for two equalizers 
h1 = win32com.client.Dispatch("TekLE320PI.LE_Manager_Cmds")
h2 = win32com.client.Dispatch("TekLE320PI.LE_Manager_Cmds")

# list all equalizers (until connection, either handle works)
(variant_bool, le_count, e_num, e_str) = h1.PI_conn_refresh()
logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))

(variant_bool, msn_list, e_num, e_str) = h1.PI_conn_avail_Q()
logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
le_list = msn_list.split(',')
print('found equalizers ...')
for i in range(le_count):
    print('index: {}, model: {}'.format(le_list[i*2], le_list[i*2+1]))

# power on all (until connection, either handle works)
for i in range(1, le_count + 1): # one-based numbering
    (variant_bool, is_on, e_num, e_str) = h1.PI_conn_power_Q(i)
    logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
    print('index: {}, is on: {}'.format(i, is_on))
    print('powering on index {} ...'.format(i))
    (variant_bool, e_num, e_str) = h1.PI_conn_power(i, True)
    logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
# disconnect handle
# PI_conn_power_Q() and PI_conn_power() calls leave communication in  
# intermediate "not-connected" and "not-disconnected" state
(variant_bool, e_num, e_str) = h1.PI_disconnect_all()
logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))


# connect to equalizers
# lower index connections will mask higher index targets
# be sure to connect to highest index first

# NOTE: PI_connect() sets target to default state

# equalizer 2, simple setup, save state
print('connect equalizer 2 ...')
(variant_bool, e_num, e_str) = h2.PI_connect(2)
logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
(variant_bool, e_num, e_str) = h2.PI_mode(1, chan, le_mode['tap4'])
logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
(variant_bool, e_num, e_str) = h2.PI_tap4_out_amp(1, chan, 2000)
logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
(variant_bool, e_num, e_str) = h2.PI_tap4_out_enable(1, chan, True)
logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
(variant_bool, e_num, e_str) = h2.PI_tap4_statefile_save(1, chan, 'mystate', True)
logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
print('equalizer 2 setup finished')

# equalizer 1, recall state (duplicate equalizer 2)
print('connect equalizer 1 ...')
(variant_bool, e_num, e_str) = h1.PI_connect(1)
logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
(variant_bool, e_num, e_str) = h1.PI_mode(1, chan, le_mode['tap4'])
logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
(variant_bool, isCompat, e_num, e_str) = h1.PI_tap4_statefile_load(1, chan, 'mystate')
logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
print('equalizer 1 setup finished')

def tap4_status(hx):
    """helper function to print equalizer 4tap mode status"""
    print('equalizer 1 status ...')
    for chan in range(1, 3):
        print('channel: {}'.format(chan))
        (variant_bool, gain, e_num, e_str) = hx.PI_tap4_agc_gain_Q(1, chan)
        logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
        print('agc_gain: {}'.format(gain))
        
        (variant_bool, agc_level, e_num, e_str) = hx.PI_tap4_agc_lev_Q(1, chan)
        logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
        print('agc_level: {}'.format(agc_level))
        
        (variant_bool, isLocked, e_num, e_str) = hx.PI_tap4_agc_state_Q(1, chan)
        logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
        print('agc_state: {}'.format(isLocked))

        (variant_bool, deemp, e_num, e_str) = hx.PI_tap4_deemph_Q(1, chan)
        logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
        print('deemph: {}'.format(deemp))
        
        (variant_bool, rate, e_num, e_str) = hx.PI_tap4_emu_rate_Q(1, chan)
        logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
        print('emu_rate: {}'.format(rate))
        
        (variant_bool, isAuto, e_num, e_str) = hx.PI_tap4_offs_state_Q(1, chan)
        logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
        print('offs_state: {}'.format(isAuto))
        
        (variant_bool, offs, e_num, e_str) = hx.PI_tap4_offs_val_Q(1, chan)
        logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
        print('offs_val: {}'.format(offs))
        
        (variant_bool, ampMv, e_num, e_str) = hx.PI_tap4_out_amp_Q(1, chan)
        logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
        print('out_amp: {}'.format(ampMv))
        
        (variant_bool, isCalib, e_num, e_str) = hx.PI_tap4_out_cal_Q(1, chan)
        logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
        print('out_cal: {}'.format(isCalib))
        
        (variant_bool, presh, e_num, e_str) = hx.PI_tap4_preshoot_Q(1, chan)
        logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
        print('preshoot: {}'.format(presh))
        
        (variant_bool, isEnabled, e_num, e_str) = hx.PI_tap4_out_enable_Q(1, chan) # enable indicator led will be active if either channel is enabled
        logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
        print('out_enable: {}'.format(isEnabled))
        
        (variant_bool, allEnabled, e_num, e_str) = hx.PI_tap4_tap_enable_all_Q(1, chan)
        logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
        print('tap_enable_all: {}'.format(allEnabled))
        for tap in range(1, 5):
            (variant_bool, isEnabled, e_num, e_str) = hx.PI_tap4_tap_enable_Q(1, chan, tap)
            logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
            (variant_bool, tap_val, e_num, e_str) = hx.PI_tap4_tap_val_Q(1, chan, tap)
            logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
            print('tap: {}, enabled: {}, value: {}'.format(tap, isEnabled, tap_val))

# show status
tap4_status(h1)
tap4_status(h2)

# disconnect (equalizer retains configuration state)
(variant_bool, e_num, e_str) = h1.PI_disconnect_all()
logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))
(variant_bool, e_num, e_str) = h2.PI_disconnect_all()
logging.debug('call return: {}, error number: {}, error message: {}'.format(variant_bool, e_num, e_str))

print('end of program')
