# Testing PI Performance  [![Python 3.6](https://img.shields.io/badge/python-3.6-&?labelColor=3E434A&colorB=006281&logo=python)](https://www.python.org/downloads/release/python-360/)

Easy to use test application for measuring PI curve query performance on Tektronix oscilloscopes. 

Supported Instruments: 

* [MSO3/4/5/6 Series Instruments](https://www.tek.com/innovative-scopes)

### Description 

Latency and Throughput tester to give repeatable measurements to monitor Programmable Interface performance. 

Example output: 

```
Latency test: :ACQUIRE:STATE ON (single sequence)->*OPC?-> MEASUREMENT:MEAS1:VALUE? (waveform display off for 4/5/6 series)
Record length: 1000
Number of loops: 10
Loop times (seconds): [0.208, 0.231, 0.181, 0.148, 0.139, 0.137, 0.161, 0.176, 0.191, 0.152]
Sorted loop times: [0.137, 0.139, 0.148, 0.152, 0.161, 0.176, 0.181, 0.191, 0.208, 0.231]
Average loop time: 0.172s (stddev=0.0294)
Median loop time: 0.168s
Loops per second: 5.96 (stddev=0.958)
```

```
Throughput test: CURVE? while acquisition running (waveform display off for 4/5/6 series)
Record length: 1000
Number of loops: 10
Loop times (seconds): [0.0264, 0.0147, 0.0178, 0.0139, 0.0122, 0.0481, 0.0576, 0.0106, 0.012, 0.00833]
Sorted loop times: [0.00833, 0.0106, 0.012, 0.0122, 0.0139, 0.0147, 0.0178, 0.0264, 0.0481, 0.0576]
Average loop time: 0.0222s (stddev=0.0162)
Median loop time: 0.0143s
Loops per second: 65.2 (stddev=31.0)
Bytes per loop: [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
Average bytes per loop: 1000.0
Throughput (MB/s): 0.0652 (stddev=0.031)
```

### Installation

First, make sure you have python installed and ensure that pip, setuptools and wheel are up to date:

 `python -m pip install --upgrade pip setuptools wheel`

Create a virtual environment to install required packages into an isolated location

```
$ python3 -m venv visa_env

$ source visa_env/bin/activate

$pip install -r requirements.txt

```

### Usage: 

test_pi_performance.py \<args\>

positional arguments:

* resource_expression   The resource_expression of the device to be connected to, provided as a valid TCPIP resource expression.

  e.g. TCPIP::10.0.0.17::INSTR 

  Supported connection types: TCPIP, USBTMC, SOCKET

* optional arguments:
    -h, --help  show this help message and exit.  
    -l \<LOOPS\>, --loops \<LOOPS\>  Number of times each test is run (default=25)  
    -r \<RECORDLENGTH\>, --recordlength \<RECORDLENGTH\> Horizontal record length (default=10000)  
    -v, --verbose  Enables messages for PI commands and responses.  
    -s, --single  Enables CURVE? testing of a single, stopped acquisition.  
    -d, --displayoff  Disables channel display. (Only supported on MSO4/5/6 Series)  
    -p, --pyvisa  Connect via pyvisa-py.

E.g: 

`python test_pi_performance.py -r 1000 -l 10 -v -d -p TCPIP::10.0.0.17::INSTR`

