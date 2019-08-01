# Python3 PPG User Pattern
# https://www.tek.com/sample-license

# two commands are available for loading user patterns

# digital[1|2|3|4]:pattern:data
# pattern data is ascii 1s and 0s
# convenient but inefficient (one byte of work for one bit of pattern)

# digital[1|2|3|4]:pattern:hdata
# pattern data is ascii hexadecimal
# more efficient (one byte of work for four bits of pattern)

import time # std module
import visa # http://github.com/pyvisa/pyvisa

visa_address = 'USB::0x0699::0x3132::9211157::INSTR'

# example patterns
my_pat_txt = '0100000101010010'
my_pat_txt_len = 16 # bits
my_pat_bin = 0b0100000101010010
my_pat_bin_len = 16 # bits

# data conversion
def binary_block_header(byte_count):
    """returns a binary block header string for a given byte count"""
    header = '#{:d}{:d}'.format(len(str(byte_count)), byte_count)
    return header

my_pat_txt_header = binary_block_header(len(my_pat_txt))
my_pat_txt_binblock = '{header:s}{pattern:s}'.format(
    header = my_pat_txt_header,
    pattern = my_pat_txt)

my_pat_hex = '{:x}'.format(my_pat_bin)
my_pat_hex_header = binary_block_header(len(my_pat_hex))
my_pat_hex_binblock = '{header:s}{pattern:s}'.format(
    header = my_pat_hex_header,
    pattern = my_pat_hex)

my_pat2_txt_header = binary_block_header(len(my_pat2_txt))
my_pat2_txt_binblock = '{header:s}{pattern:s}'.format(
    header = my_pat2_txt_header,
    pattern = my_pat2_txt)

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
while r != '0, No error\n':
    r = ppg.query('system:error?')
    i += 1
print('messages cleared: {}'.format(i))

r = ppg.query('*idn?')
print(r.strip())

ppg.write('digital1:pattern:type DATA') # user pattern
ppg.write('digital1:pattern:length {total_bits:d}'.format(
    total_bits = my_pat2_txt_len))
ppg.write('digital1:pattern:data {offset:d},{write_bits:d},{binblock:s}'.format(
    offset = 1,
    write_bits = my_pat2_txt_len,
    binblock = my_pat2_txt_binblock))

ppg.write('digital2:pattern:type DATA') # user pattern
ppg.write('digital2:pattern:length {total_bits:d}'.format(
    total_bits = my_pat2_txt_len))
ppg.write('digital2:pattern:data {offset:d},{write_bits:d},{binblock:s}'.format(
    offset = 1,
    write_bits = my_pat2_txt_len,
    binblock = my_pat2_txt_binblock))

# print status
r = ppg.query('system:error?')
print('status: {}'.format(r.strip()))
while r != '0, No error\n':
    r = ppg.query('system:error?')
    print(r.strip())
