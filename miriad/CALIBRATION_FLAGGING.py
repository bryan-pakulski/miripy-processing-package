from . import *
from . import FLAGGING

# Contains basic calibration methods
class BCF(FLAGGING.FLAGGING):

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
		self.image_calibration()

	# Calibration / Cleaning in preperation for imaging
	def image_calibration(self):

		print("Preparing for imaging")

		# Create subfolder for imaging, increment ID by + 1 if another folder exists
		i = 0
		while os.path.exists(self.SETTINGS["working_directory"] + self.IMAGE_DATA + "-BIMG-%s" % i):
			i += 1

		self.IMAGE_OUTPUT = self.SETTINGS["working_directory"] + self.IMAGE_DATA + "-BIMG-" + str(i) + "/"
		os.mkdir(self.IMAGE_OUTPUT)
		
		# Average gain solutions
		interval = input("Enter minute interval of phase calibration used again average gain for imaging: ")
		miriad_command(
		"gpaver",
		{
			"vis" : self.SETTINGS["working_directory"] + self.IMAGE_DATA,
			"interval" : interval
		})

		# Remove basic RFI
		print("Removing RFI")

		stage = 1
		while (1):

			# Preview data
			miriad_command(
			"uvspec",
			{
				"vis" : self.SETTINGS["working_directory"] + self.IMAGE_DATA,
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
				self.basic_flagging(self.SETTINGS["working_directory"] + self.IMAGE_DATA)
				stage += 1
		
		# Apply calibration and save to output data
		print("Applying calibration to image data")
		miriad_command(
		"uvaver",
		{
			"vis" : self.SETTINGS["working_directory"] + self.IMAGE_DATA,
			"stokes" : "xx,yy",
			"out" : self.IMAGE_OUTPUT + "img.uvav"
		})

		# Split channels
		cwd = os.getcwd()
		os.chdir(self.IMAGE_OUTPUT)
		maxwidth = input("Enter max imaging bandwidth per dataset (in Ghz i.e. 0.512): ")
		miriad_command(
		"uvsplit",
		{
			"vis" : "img.uvav",
			"maxwidth" : maxwidth
		})
		os.chdir(cwd)
	
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
			"options" : "xyvary,qusolve"
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


		input("Enter to continue")

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
			"options" : "xyvary,qusolve"
		})

		# Check that scaling factors were applied correctly
		miriad_command(
		"gpboot",
		{
			"vis" : self.SETTINGS["working_directory"] + self.SECONDARY_CAL,
			"cal" : self.SETTINGS["working_directory"] + self.PRIMARY_CAL,
		})
		print("Scaling values for each individual bin should be ~0.95")

		# Copy valiues from phase calibrator to source image
		miriad_command(
		"gpcopy",
		{
			"vis" : self.SETTINGS["working_directory"] + self.SECONDARY_CAL,
			"out" : self.SETTINGS["working_directory"] + self.IMAGE_DATA,
		})

		print("Calibration Complete with the following: ")
		print("Bandpass / Flux calibration completed in primary: ", self.PRIMARY_CAL)
		print("Phase calibration completed in secondary: ", self.SECONDARY_CAL)
		print("Imaging prepared for: ", self.IMAGE_DATA)

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