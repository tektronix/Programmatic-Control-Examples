# Python3 PPG User Pattern Long
# https://www.tek.com/sample-license

# demonstrate successive pattern writes to work within a 1024 byte maximum
# binary block header size

import time # std module
import re # std module
import visa # http://github.com/pyvisa/pyvisa

visa_address = 'USB::0x0699::0x3132::9211157::INSTR'

# long pattern
my_pat = ('3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa'
          'a6a5a9871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871'
          'e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e387'
          '1e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e38'
          '71e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3'
          '871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e'
          '3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871'
          'e3871e3871e3871e3871e3871e3871e3871e3870bc78f4aaaaaaaaaaaaaaaaaa'
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa15555e3871e3871e1'
          'ab9c9686e6c16aaa9aa63eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa'
          '2aaaaa3eaa2aaaaa3eaaa6a5a9871e3871e3871e3871e3871e3871e3871e3871'
          'e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e387'
          '1e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e38'
          '71e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3'
          '871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e'
          '3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871'
          'e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3870bc78'
          'f4aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
          'aaa15555e3871e3871e1ab9c9686e6c16aaa9aa63eaa2aaaaa3eaa2aaaaa3eaa'
          '2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaaa6a5a9871e3871e3871e3871'
          'e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e387'
          '1e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e38'
          '71e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3'
          '871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e'
          '3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871'
          'e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e387'
          '1e3871e3871e3870bc78f4aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
          'aaaaaaaaaaaaaaaaaaaaaaa15555e3871e3871e1ab9c9686e6c16aaa9aa63eaa'
          '2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaaa6a5'
          'a9871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e387'
          '1e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e38'
          '71e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3'
          '871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e'
          '3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871'
          'e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e387'
          '1e3871e3871e3871e3871e3871e3871e3870bc78f4aaaaaaaaaaaaaaaaaaaaaa'
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa15555e3871e3871e1ab9c'
          '9686e6c16aaa9aa63eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa2aaa'
          'aa3eaa2aaaaa3eaaa6a5a9871e3871e3871e3871e3871e3871e3871e3871e387'
          '1e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e38'
          '71e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3'
          '871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e'
          '3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871'
          'e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e387'
          '1e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3870bc78f4aa'
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa1'
          '5555e3871e3871e1ab9c9686e6c16aaa9aa63eaa2aaaaa3eaa2aaaaa3eaa2aaa'
          'aa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaaa6a5a9871e3871e3871e3871e387'
          '1e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e38'
          '71e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3'
          '871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e'
          '3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871'
          'e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e387'
          '1e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e38'
          '71e3871e3870bc78f4aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
          'aaaaaaaaaaaaaaaaaaa15555e3871e3871e1ab9c9686e6c16aaa9aa63eaa2aaa'
          'aa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaaa6a5a987'
          '1e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e38'
          '71e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3'
          '871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e'
          '3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871'
          'e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e387'
          '1e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e38'
          '71e3871e3871e3871e3871e3871e3870bc78f4aaaaaaaaaaaaaaaaaaaaaaaaaa'
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa15555e3871e3871e1ab9c9686'
          'e6c16aaa9aa63eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3eaa2aaaaa3e'
          'aa2aaaaa3eaaa6a5a9871e3871e3871e3871e3871e3871e3871e3871e3871e38'
          '71e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3'
          '871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e'
          '3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871'
          'e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e387'
          '1e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e3871e38'
          '71e3871e3871e3871e3871e3871e3871e3871e3871e3871e3870bc78f4aaaaaa'
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa15555'
          'e3871e3871e1ab9c9686e6c16aaa9aa6')

not_hex = re.compile(r'[^0-9a-f]', re.IGNORECASE)

def binary_block_header(byte_count):
    '''returns a binary block header string for a given byte count'''
    if byte_count > 1024:
        raise Exception('ppg maximum binary block header is 1024. {:d} bytes requires subdivision.'.format(byte_count))
    header = '#{:d}{:d}'.format(len(str(byte_count)), byte_count)
    return header

def write_hex_pat_slice(channel, start_bit, pat_slice):
    '''writes hex string "pat_slice" starting at "start_bit"'''
    byte_count = len(pat_slice)
    ppg.write('digital{chan:d}:pattern:hdata {start:d},{bit_count:d},{bbh:s}{dat:s}'.format(
        chan = channel,
        start = start_bit,
        bit_count = byte_count * 4,
        bbh = binary_block_header(byte_count),
        dat = pat_slice))

def write_hex_pat(channel, pattern):
    '''calculates and executes slices and writes to send hex string "pattern"'''
    # check hex chars
    if re.search(not_hex, pattern):
        raise Exception('pattern string contains non-hex characters')
    # check length
    hex_len = len(pattern)
    bit_len = hex_len * 4
    if bit_len > 4194304:
        raise Exception('pattern length exceeds 4,194,304 bits')
    # calculate division of writes for full pattern
    w, r = divmod(hex_len, 1024)
    i = 0
    if w > 0:
        for i in range(w):
            offset_hex = i * 1024
            start_bit = (offset_hex * 4) + 1 # one-based numbering
            write_hex_pat_slice(channel, start_bit, pattern[offset_hex:offset_hex+1024])
        i += 1
    if r > 0:
        offset_hex = i * 1024
        start_bit = (offset_hex * 4) + 1 # one-based numbering
        write_hex_pat_slice(channel, start_bit, pattern[offset_hex:])
    # set len
    ppg.write('digital{chan:d}:pattern:length {leng:d}'.format(
        chan = channel,
        leng = bit_len))

# instrument connection
rm = visa.ResourceManager()
ppg = rm.open_resource(visa_address)
ppg.timeout = 30000 # ms
ppg.encoding = 'latin_1'
ppg.read_termination = '\n'
ppg.write_termination = None

# clear messages by reading all
r = ppg.query('system:error?')
i = 0
while r != '0, No error':
    r = ppg.query('system:error?')
    i += 1
print('messages cleared: {}'.format(i))

r = ppg.query('*idn?')
print(r)

write_hex_pat(1, my_pat)

# print status
r = ppg.query('system:error?')
print('status: {}'.format(r.strip()))
while r != '0, No error':
    print(ppg.query('system:error?'))

