from . import *

# Contains basic calibration methods
class BCF():

	def __init__(self, settings):

		self.SETTINGS = settings

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

	def process(self):
		print("Beginning calibration")

		stage = 1
		while (1):

			# Preview data
			miriad_command(
			"uvspec",
			{
				"vis" : self.SETTINGS["working_directory"] + self.PRIMARY_CAL,
				"stokes": "xx,yy",
				"axis" : "chan,amp",
				"device" : "/xs"
			})

			in_str = "Perform pass " + str(stage) + " of calibration? (0) yes - (1) no "
			lp = ""
			
			while (lp != "0" and lp != "1"):
				lp = input(in_str)

			if (lp == "1"):
				break

			elif (lp == "0"):
				# Determine bandpass shape
				print("Determining bandpass shape")
				miriad_command(
				"mfcal",
				{
					"vis" : self.SETTINGS["working_directory"] + self.PRIMARY_CAL
				})

				# Flag RFI
				miriad_command(
				"pgflag",
				{
					"vis" : self.SETTINGS["working_directory"] + self.PRIMARY_CAL,
					"stokes" : "xx,yy",
					"device" : "/xs",
					"command" : "\<b"
				})

				miriad_command(
				"pgflag",
				{
					"vis" : self.SETTINGS["working_directory"] + self.PRIMARY_CAL,
					"stokes" : "yy,xx",
					"device" : "/xs",
					"command" : "<b"
				})

				# Manually flag RFI data
				print("(p) for polygon select (x) to confirm polygon (r) to redraw (x) to quit")
				miriad_command(
				"blflag",
				{
					"vis" : self.SETTINGS["working_directory"] + self.PRIMARY_CAL,
					"device" : "/xs",
					"stokes" : "xx,yy",
					"axis" : "chan,amp",
					"options" : "nofqav,nobase"
				})

				stage += 1

# Contains more advanced calibration methods
class ACF():

	def __init__(self, settings):

		self.SETTINGS = settings

		print("Initialising advanced calibration flagging")
		
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

	def process(self):
		print("Processing")