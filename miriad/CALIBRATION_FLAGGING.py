from . import *

# Contains basic calibration methods
class BCF():

    def __init__(self, dataset):
        print("Initialising basic calibration flagging")
        self.process(dataset)

    def process(self, dataset):
        print("Processing")

        miriad_command(
        "atlod",
        {
            "in": "input_file",
            "out": "output" + ".uv",
            "ifsel":"1",
            "options":"birdie,rfiflag,noauto,xycorr"
        })



# Contains more advanced calibration methods
class ACF():

    def __init__(self, dataset):
        print("Initialising advanced calibration flagging")
        self.process(dataset)

    def process(self, dataset):
        print("Processing")