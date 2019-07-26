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

	# Processing steps
	def process(self):
		self.bandpass_flux_calibration()
		self.phase_calibration()

	# Basic RFI flagging steps for calibration
	def basic_flagging(self, vis_source):

		# Determine bandpass shape
		print("Determining bandpass shape")
		miriad_command(
		"mfcal",
		{
			"vis" : vis_source
		})

		# Flag RFI
		miriad_command(
		"pgflag",
		{
			"vis" : vis_source,
			"stokes" : "xx,yy",
			"device" : "/xs",
			"command" : "<b"
		})

		miriad_command(
		"pgflag",
		{
			"vis" : vis_source,
			"stokes" : "yy,xx",
			"device" : "/xs",
			"command" : "<b"
		})

		# Manually flag RFI data
		print("(p) for polygon select (x) to confirm polygon (r) to redraw (x) to quit")
		miriad_command(
		"blflag",
		{
			"vis" : vis_source,
			"device" : "/xs",
			"stokes" : "xx,yy",
			"axis" : "chan,amp",
			"options" : "nofqav,nobase"
		})

	
	# Calibration of bandpass / flux channels
	def bandpass_flux_calibration(self):

		print("Beginning bandpass / flux calibration")

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

			# Exit calibration
			if (lp == "1"):
				break

			# Perform another flagging pass
			elif (lp == "0"):
				self.basic_flagging(self.SETTINGS["working_directory"] + self.PRIMARY_CAL)
				stage += 1
			
		# Perform gain calibration
		interval = input("Select interval (0.1 = 10 second cycles): ")
		nfbin = input("Select bin count (splits frequency of observation into chunks i.e. 2048 / 4 = 512Mhz chunks): ")

		miriad_command(
		"gpcal",
		{
			"vis" : self.SETTINGS["working_directory"] + self.PRIMARY_CAL,
			"interval" : interval,
			"nfbin" : nfbin,
			"options" : "xyvary"
		})

		# Display phase plot against time
		miriad_command(
		"uvplt",
		{
			"vis" : self.SETTINGS["working_directory"] + self.PRIMARY_CAL,
			"stokes" : "xx,yy",
			"axis" : "real,imag",
			"options" : "nofqav,nobase,equal",
			"device" : "/xs"
		})

		# Copy data to secondary cal
		miriad_command(
		"gpcopy",
		{
			"vis" : self.SETTINGS["working_directory"] + self.PRIMARY_CAL,
			"out" : self.SETTINGS["working_directory"] + self.SECONDARY_CAL,
		})


	# Phase calibration in preperation of imaging
	def phase_calibration(self):
		
		print("Beginning phase calibration")

		stage = 1
		while (1):

			# Preview data
			miriad_command(
			"uvspec",
			{
				"vis" : self.SETTINGS["working_directory"] + self.SECONDARY_CAL,
				"stokes": "xx,yy",
				"axis" : "chan,amp",
				"device" : "/xs"
			})

			in_str = "Perform pass " + str(stage) + " of calibration? (0) yes - (1) no "
			lp = ""
			
			while (lp != "0" and lp != "1"):
				lp = input(in_str)

			# Exit calibration
			if (lp == "1"):
				break

			# Perform another flagging pass
			elif (lp == "0"):
				self.basic_flagging(self.SETTINGS["working_directory"] + self.SECONDARY_CAL)
				stage += 1
		
		# Perform gain calibration
		interval = input("Select interval (0.1 = 10 second cycles): ")
		nfbin = input("Select bin count (splits frequency of observation into chunks i.e. 2048 / 4 = 512Mhz chunks): ")

		miriad_command(
		"gpcal",
		{
			"vis" : self.SETTINGS["working_directory"] + self.SECONDARY_CAL,
			"interval" : interval,
			"nfbin" : nfbin,
			"options" : "xyvary"
		})

		# Check that scaling factors were applied correctly
		miriad_command(
		"gpboot",
		{
			"vis" : self.SETTINGS["working_directory"] + self.SECONDARY_CAL,
			"cal" : self.SETTINGS["working_directory"] + self.PRIMARY_CAL,
		})
		print("Scaling values for each individual bin should be ~0.95")

	# Imaging phase
	def imaging(self):
		pass


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