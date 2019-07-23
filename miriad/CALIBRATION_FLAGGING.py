from . import *

# Contains basic calibration methods
class BCF():

    def __init__(self, settings):
        print("Initialising basic calibration flagging")
        
        # Select calibration datasets
        calibration_selection = {}

        i = 0
        for f in os.listdir(settings["working_directory"]):
            calibration_selection[str(i)] = f
            i += 1

        print(calibration_selection)

        self.PRIMARY_CAL = calibration_selection[ input("Enter selection of primary calibration dataset: ") ]
        self.SECONDARY_CAL = calibration_selection[ input("Enter selection of secondary calibration dataset: ") ]
        self.IMAGE_DATA = calibration_selection[ input("Enter selection of imaging dataset: ") ]

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