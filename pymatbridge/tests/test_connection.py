import pymatbridge as pymat

def test_connection():
    matlab = pymat.Matlab()
    matlab.start()

    assert matlab.is_connected(), "Connection failed"
    matlab.stop()
    assert not matlab.is_connected(), "Disconnection failed"

