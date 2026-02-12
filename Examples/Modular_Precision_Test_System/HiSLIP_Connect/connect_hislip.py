import pyvisa
from pyvisa import errors as visa_errors

rm = None
inst = None

try:
    rm = pyvisa.ResourceManager()
    inst = rm.open_resource("TCPIP0::192.168.0.50::hislip0::INSTR")

    # Configure I/O *before* using the session
    inst.write_termination = "\n"
    inst.read_termination = "\n"
    inst.send_end = True
    inst.timeout = 10_000  # ms

    # Best-effort clear
    try:
        inst.clear()
    except visa_errors.VisaIOError as e:
        print(f"Warning: clear() failed: {e}")

    inst.write("login admin")
    print(inst.query("*IDN?").strip())

    inst.write("logout")

except visa_errors.VisaIOError as e:
    print(f"VISA I/O error: {e}")
except visa_errors.InvalidSession as e:
    print(f"Invalid session: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    # Always attempt to close resources if they were opened
    if inst is not None:
        try:
            inst.clear()
            inst.close()
        except Exception as e:
            print(f"Warning: inst.close() failed: {e}")
    if rm is not None:
        try:
            rm.close()
        except Exception as e:
            print(f"Warning: rm.close() failed: {e}")

