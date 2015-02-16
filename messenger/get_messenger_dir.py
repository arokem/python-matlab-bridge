import sys
import platform


def get_messenger_dir():
    # Check the system platform first
    splatform = sys.platform

    if splatform.startswith('linux'):
        messenger_dir = 'mexa64'
    elif splatform.startswith('darwin'):
        messenger_dir = 'mexmaci64'
    elif splatform.startswith('win32'):
        if splatform == "win32":
            # We have a win64 messenger, so we need to figure out if this is 32 or 64
            # bit Windows:
            if not platform.machine().endswith('64'):
                raise ValueError("pymatbridge does not work on win32")

        # We further need to differniate 32 from 64 bit:
        maxint = sys.maxsize
        if maxint == 9223372036854775807:
            messenger_dir = 'mexw64'
        elif maxint == 2147483647:
            messenger_dir = 'mexw32'
    return messenger_dir
