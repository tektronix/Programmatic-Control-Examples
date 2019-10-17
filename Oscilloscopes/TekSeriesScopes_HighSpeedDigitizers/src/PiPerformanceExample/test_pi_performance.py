"""Tests Programmable Interface (PI) latency and throughput.
"""

import visa
import socket
import argparse
from time import time, strftime, localtime
from math import log10, floor


def get_device_robust_connection(resource_expression, tries=4):
    """Retrieves the pi_object representing the connection to the device in the resource expression. The device is
    given four tries by default to regain a connection. This currently handles timeouts and old query results being
    returned.

    Arguments:
        resource_expression (str):
            The resource_expression of the device to be connected to, provided as a valid TCPIP resource expression.
        tries (int):
            Number of times a connection will be attempted default is 4.

    Returns:
        pi_object (obj):
            The connection to the device using whichever Visa library was loaded.

    Raises:
        Exception: Raised if an attempt to connect to the device failed.
        StandardError: Raised if the device is still not returning valid responses after the given number of tries.
    """
    try_num = tries
    sync_stat = ""
    pi_object = None

    for chance in range(tries):
        try:
            # Attempt to open a visa connection to the device
            # visa.log_to_screen()  # debug statement, uncomment to enable standalone pyvisa call monitoring

            pi_object = visa.ResourceManager(_visa_backend).open_resource(resource_expression)

            if pi_object.resource_class == "SOCKET":
                # Socket connections seem to need the termination characters specified, the rest will fail if you do
                pi_object.write_termination = '\n'

                if _visa_backend == "@py":
                    print("\nSOCKET connections using PyVISA (standalone) to {0} are not supported. "
                          "Aborting test suite.\n".format(resource_expression))
                    raise
                    # If we ever fiogure out why the reads stall then we will want to assign a term character
                    # for PyVISA here
                    # pi_object.read_termination = ''
                else:
                    pi_object.read_termination = '\n'

        except Exception as e:
            # Couldn't instantiate the VISA connection for some reason
            print("\nVISA connection to {0} failed due to: {1}\nAborting test suite.\n".format(resource_expression,
                                                                                               e))
            raise

        for _ in range(20):
            try:
                pi_object.timeout = 5000
                old_results = pi_object.read()
            except visa.VisaIOError:
                break
            if old_results.strip() == '':
                break

        # Reset the device because it could be in a state that will never return when *OPC? is queried.
        pi_object.write("*RST")
        pi_object.write("*OPC")

        try:
            sync_stat = pi_object.query("*OPC?").strip()
        except visa.VisaIOError as ve:
            print("\nVISA connection to {0} threw the error: {1}\nTrying Again ({2} Tries).\n"
                  .format(resource_expression, ve, try_num))
        if sync_stat == "1":
            break
        pi_object.close()
        try_num -= 1

    if try_num == 0:
        raise StandardError("An invalid string was returned during setup on the Device {0} indicating it may have "
                            "become unsynchronized. Last returned string was {1} to the query: *OPC?"
                            .format(resource_expression, sync_stat))
    return pi_object


def pi_query(pi_object, cmd, binary=False):
    """Queries the device with the provided command and returns the result.

    Arguments:
        pi_object (obj):
            The connection to the device using whichever Visa library was loaded.
        cmd (str):
            The PI query to be sent to the device.
        binary (Optional[bool]):
            A flag to decide if response should be in binary format.

    Returns:
        str, float: The return data from the PI query and the time for the response.
    """
    if args.verbose:
        print("{0} - Query >>  {1}".format(strftime("%Y-%m-%d %H:%M:%S", localtime()), repr(cmd)))

    try:
        start_time = time()
        if binary:
            response = pi_object.query_binary_values(cmd)
        else:
            response = pi_object.query(cmd)
        end_time = time()
        elapsed_time = end_time - start_time

    except (visa.VisaIOError, socket.error) as e:
        print("\nThe PI query for {0} failed with the following message: {1}"
              "\nMake sure a signal is connected to channel 1 on the device.\n".format(repr(cmd), repr(e)))
        raise

    if args.verbose:
        print("{0} - Response from {1} >>  {2}".format(strftime("%Y-%m-%d %H:%M:%S", localtime()), cmd, repr(response)))
    return response, elapsed_time


def pi_write(pi_object, cmd):
    """Queries the device with the provided command and returns the result.

    Arguments:
        pi_object (obj):
            The connection to the device using whichever Visa library was loaded.
        cmd (str):
            The PI query to be sent to the device.

    Returns:
        float: The time to write.
    """
    if args.verbose:
        print("{0} - Write >>  {1}".format(strftime("%Y-%m-%d %H:%M:%S", localtime()), repr(cmd)))

    try:
        start_time = time()
        pi_object.write(cmd)
        end_time = time()
        elapsed_time = end_time - start_time

    except (visa.VisaIOError, socket.error) as e:
        print("The PI write for {0} failed with the following message: {1}".format(repr(cmd), repr(e)))
        raise

    return elapsed_time


def median(data):
    """Returns the median of data.

    Arguments:
        data (list):
            A list of numbers.

    Returns:
        float: Median of the provided data.
    """
    n = len(data)
    if n < 1:
        return None
    if n % 2 == 1:
        return sorted(data)[n//2]
    else:
        return sum(sorted(data)[n//2-1:n//2+1])/2.0


def mean(data):
    """Return the sample arithmetic mean of data.

    Arguments:
        data (list):
            A list of numbers.

    Returns:
        float: Mean of the provided data.
    """
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data.

    Arguments:
        data (list):
            A list of numbers.

    Returns:
        float: Sum of square deviations of the data.
    """
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss


def stddev(data, ddof=0):
    """Returns population standard deviation or sample standard deviation.

    Returns sample standard deviation when ddof=1

    Arguments:
        data (list):
            A list of numbers.
        ddof (int):
            Delta degrees of freedom.


    Returns:
        float: Standard deviation of the data
    """
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/(n-ddof)
    return pvar**0.5


def round_significant_figures(number_to_round, significant_figures):
    """This function takes number_to_round and significant_figures and returns rounded_number with the appropriate
    quantity of significant figures.

    Arguments:
        number_to_round (float):
            The number that's being rounded.
        significant_figures (int):
            The number of significant figures to round to.

    Returns:
        float: A rounded number with the appropriate quantity of significant figures.
    """
    if number_to_round == 0:  # Check if number_to_round is 0 before doing log10
        return 0  # Python's round() would return 0.0 instead
    absolute_number = abs(number_to_round)
    rounded_number = round(number_to_round, significant_figures - int(floor(log10(absolute_number))) - 1)
    decimal_index = str(absolute_number).find('.')
    if decimal_index == -1:  # If there is no decimal
        decimal_index = len(str(absolute_number))  # Set decimal_index to be after the last digit
    if decimal_index >= significant_figures:
        return int(rounded_number)  # Return an int if not rounding after the decimal
    return rounded_number


def get_parsed_arguments():
    """This function parses a resource_expression argument and other optional arguments for this script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("resource_expression", help="The resource_expression of the device to be connected to, "
                             "provided as a valid TCPIP resource expression.")
    parser.add_argument("-l", "--loops", type=int, help="Number of times each test is run (default=25)", default=25)
    parser.add_argument("-r", "--recordlength", type=int, help="Horizontal record length (default=10000)",
                        default=10000)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enables messages for PI commands and responses.",
                        default=False)
    parser.add_argument("-s", "--single", action="store_true", help="Enables CURVE? testing of a single, "
                                                                    "stopped acquisition.", default=False)
    parser.add_argument("-d", "--displayoff", action="store_true", help="Disables channel display.", default=False)
    parser.add_argument("-p", "--pyvisa", action="store_true", help="Connect via pyvisa-py.", default=False)
    args = parser.parse_args()

    if args.loops < 1:
        raise argparse.ArgumentError("Loop count should be greater than 0")
    if args.recordlength < 1:
        raise argparse.ArgumentError("Record length should be greater than 0")

    return args


def setup_latency_test(pi_object):
    """This function sets up the device for a PI latency test.

    Arguments:
        pi_object (obj):
            The connection to the device using whichever Visa library was loaded.
    """
    pi_write(pi_object, "*RST")
    pi_query(pi_object, "*OPC?")
    pi_write(pi_object, "AUTOSET EXECUTE")
    pi_query(pi_object, "*OPC?")
    pi_write(pi_object, "ACQUIRE:STATE OFF")
    pi_write(pi_object, "HORIZONTAL:MODE MANUAL")  # This enables 5 series instruments to set record length
    pi_write(pi_object, "HORIZONTAL:RECORDLENGTH {}".format(args.recordlength))
    pi_write(pi_object, "ACQUIRE:MODE SAMPLE")
    pi_write(pi_object, "ACQUIRE:STOPAFTER SEQUENCE")
    pi_write(pi_object, "MEASUREMENT:MEAS1:TYPE PERIOD")
    pi_write(pi_object, "MEASUREMENT:MEAS1:SOURCE CH1")
    # This turns on the measurement for 4k instruments. 5 series will turn on when measurement type is set (above).
    pi_write(pi_object, "MEASUREMENT:MEAS1:STATE ON")
    if args.displayoff:
        pi_write(pi_object, "DISPLAY:WAVEFORM OFF")  # Only on 5 series
    pi_query(pi_object, "*OPC?")


def setup_throughput_test(pi_object, single=False):
    """This function sets up the device for a PI throughput test.

    Arguments:
        pi_object (obj):
            The connection to the device using whichever Visa library was loaded.
        single (bool):
            A flag to decide if CURVE? test should be done on a single, stopped acquisition.
    """
    pi_write(pi_object, "*RST")
    pi_query(pi_object, "*OPC?")
    pi_write(pi_object, "AUTOSET EXECUTE")
    pi_query(pi_object, "*OPC?")
    pi_write(pi_object, "ACQUIRE:MODE SAMPLE")
    if single:
        pi_write(pi_object, "ACQuire:STATE OFF")
        pi_write(pi_object, "ACQUIRE:STOPAFTER SEQUENCE")
    pi_write(pi_object, "HORIZONTAL:MODE MANUAL")  # This enables 5 series instruments to set record length
    pi_write(pi_object, "HORIZONTAL:RECORDLENGTH {}".format(args.recordlength))
    pi_write(pi_object, "DATA:ENCDG BINARY")
    pi_write(pi_object, "WFMOUTPRE:BYT_NR 1")
    pi_write(pi_object, "DATA:START 1")
    pi_write(pi_object, "DATA:STOP {}".format(args.recordlength))
    pi_query(pi_object, "WFMOUTPRE?")
    if args.displayoff:
        pi_write(pi_object, "DISPLAY:WAVEFORM OFF")  # Only on 5 series
    pi_query(pi_object, "*OPC?")


def latency_test_elapsed_time(pi_object):
    """This function runs a PI latency test and returns the elapsed time.

    Arguments:
        pi_object (obj):
            The connection to the device using whichever Visa library was loaded.

    Returns:
        float: Elapsed time for PI commands and queries.
    """
    if args.verbose:
        print("\n***START OF LOOP***")
    elapsed_time = pi_write(pi_object, ":ACQUIRE:STATE ON")
    elapsed_time += pi_query(pi_object, "*OPC?")[1]
    elapsed_time += pi_query(pi_object, "MEASUREMENT:MEAS1:VALUE?")[1]
    elapsed_time = round_significant_figures(elapsed_time, number_of_significant_figures)
    if args.verbose:
        print("Approximate loop time: {}s\n***END OF LOOP***\n".format(elapsed_time))
    return elapsed_time


def throughput_test_info(pi_object, single=False):
    """This function runs a PI throughput test and returns query response data and elapsed time.

    Arguments:
        pi_object (obj):
            The connection to the device using whichever Visa library was loaded.
        single (bool):
            A flag to decide if CURVE? test should be done on a single, stopped acquisition.

    Returns:
        str, float: Query response data and elapsed time for PI commands and queries.
    """
    elapsed_time = 0

    if args.verbose:
        print("\n***START OF LOOP***")

    if single:
        elapsed_time += pi_write(pi_object, ":ACQUIRE:STATE ON")
        elapsed_time += pi_query(pi_object, "*OPC?")[1]

    floats_list, curve_time = pi_query(pi_object, "CURVE?", binary=True)
    elapsed_time += curve_time
    elapsed_time = round_significant_figures(elapsed_time, number_of_significant_figures)


    if args.verbose:
        print("Approximate loop time: {}s\n***END OF LOOP***\n".format(elapsed_time))

    return floats_list, elapsed_time


def print_loop_time_stats(loop_times):
    """This function prints statistics for a list of loop times.

    Prints the loop times list, prints a sorted loop times list, prints average loop times w/ stddev, prints median loop
    time, and prints average loops per second w/ stddev.

    Arguments:
        loop_times (list):
            List of loop times.
    """
    loop_frequencies = []
    for loop_time in loop_times:
        loop_frequencies.append(1.0 / loop_time)

    average_loop_time = round_significant_figures(mean(loop_times), number_of_significant_figures)
    loop_time_stddev = round_significant_figures(stddev(loop_times), number_of_significant_figures)
    average_loop_frequency = round_significant_figures(mean(loop_frequencies), number_of_significant_figures)
    loop_frequency_stddev = round_significant_figures(stddev(loop_frequencies), number_of_significant_figures)

    print("Number of loops: {}".format(args.loops))
    print("Loop times (seconds): {}".format(loop_times))
    print("Sorted loop times: {}".format(sorted(loop_times)))
    print("Average loop time: {}s (stddev={})".format(average_loop_time, loop_time_stddev))
    print("Median loop time: {}s".format(round_significant_figures(median(loop_times),
                                                                   number_of_significant_figures)))
    print("Loops per second: {} (stddev={})".format(average_loop_frequency, loop_frequency_stddev))


def print_byte_stats(loop_times, byte_count_list):
    """This function prints statistics for a list of byte counts.

    Prints the list, the list average, and throughput (MB/s) w/ stddev.

    Arguments:
        loop_times (list):
            List of loop times.
        byte_count_list (list):
            List of byte counts.
    """
    throughputs = []
    for index, byte_count in enumerate(byte_count_list):
        throughputs.append(round_significant_figures(byte_count / loop_times[index] * MILLIONTH,
                                                     number_of_significant_figures))

    average_bytes_per_loop = mean(byte_count_list)
    average_throughput = round_significant_figures(mean(throughputs), number_of_significant_figures)
    throughput_stddev = round_significant_figures(stddev(throughputs), number_of_significant_figures)

    print("Bytes per loop: {}".format(byte_count_list))
    print("Average bytes per loop: {}".format(average_bytes_per_loop))
    print("Throughput (MB/s): {} (stddev={})".format(average_throughput, throughput_stddev))


if __name__ == "__main__":
    # Initialize variables
    _visa_backend = ""
    number_of_significant_figures = 3
    MILLIONTH = 0.000001
    BYTES_IN_FLOAT = 4
    latency_test_times = []
    throughput_test_times = []
    throughput_single_test_times = []
    throughput_bytes_list = []
    throughput_single_bytes_list = []
    display_off_string = ""

    # Parse arguments for this script
    args = get_parsed_arguments()
    if args.displayoff:
        display_off_string = " (waveform display off for 5 series)"
    if args.pyvisa:
        _visa_backend = "@py"

    # Connect to the device specified by the resource_expression argument
    print("Connecting to device...")
    pi_object = get_device_robust_connection(args.resource_expression)
    pi_object.timeout = 10000

    # Setup the device to run the loops for the latency test
    print("Setting up latency test...")
    setup_latency_test(pi_object)

    # In each loop, get the elapsed time for a latency test
    print("Running latency test...")
    for _ in range(args.loops):
        latency_elapsed_time = latency_test_elapsed_time(pi_object)
        latency_test_times.append(latency_elapsed_time)

    # Setup the device to run the loops for the throughput test
    print("Setting up throughput test...")
    setup_throughput_test(pi_object)

    print("Running throughput test...")
    for _ in range(args.loops):
        floats_list, elapsed_time = throughput_test_info(pi_object)
        throughput_bytes_list.append(len(floats_list) * BYTES_IN_FLOAT)
        throughput_test_times.append(elapsed_time)

    if args.single:
        # Setup the device to run the loops for the throughput test for single, stopped acquisitions
        print("Setting up throughput test for single, stopped acquisitions...")
        setup_throughput_test(pi_object, args.single)

        print("Running throughput test for single, stopped acquisitions...")
        for _ in range(args.loops):
            floats_list, elapsed_time = throughput_test_info(pi_object, args.single)
            throughput_single_bytes_list.append(len(floats_list) * BYTES_IN_FLOAT)
            throughput_single_test_times.append(elapsed_time)


    # Latency test results
    print("\nLatency test: :ACQUIRE:STATE ON (single sequence)  ->  *OPC?  ->  MEASUREMENT:MEAS1:VALUE?{}"
          .format(display_off_string))
    print("Record length: {}".format(args.recordlength))
    print_loop_time_stats(latency_test_times)

    # Throughput test results
    print("\nThroughput test: CURVE? while acquisition running{}".format(display_off_string))
    print("Record length: {}".format(args.recordlength))
    print_loop_time_stats(throughput_test_times)
    print_byte_stats(throughput_test_times, throughput_bytes_list)

    if args.single:
        # Throughput test results for a single, stopped acquisition

        print("\nThroughput test: :ACQUIRE:STATE ON (single sequence)  ->  *OPC?  ->  CURVE?{}"
              .format(display_off_string))
        print("Record length: {}".format(args.recordlength))
        print_loop_time_stats(throughput_single_test_times)
        print_byte_stats(throughput_single_test_times, throughput_single_bytes_list)

