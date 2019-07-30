from . import *
from . import FLAGGING

# Basic imaging class
class BIM(FLAGGING.FLAGGING):

	def __init__(self, settings):

		self.SETTINGS = settings
		self.IMAGE_OUTPUT = self.SETTINGS["working_directory"]

		print("Initialising basic imaging")
		
		# Select calibration datasets
		calibration_selection = {}

		i = 0
		for f in os.listdir(settings["working_directory"]):
			calibration_selection[str(i)] = f
			i += 1

		print(calibration_selection)

		self.IMAGE_DATA = calibration_selection[ input("Enter selection of imaging dataset: ") ]

		# Create subfolder for imaging, increment ID by + 1 if another folder exists
		i = 0
		while os.path.exists(self.IMAGE_DATA+"-B_IMAGE-%s" % i):
			i += 1
		
		self.IMAGE_OUTPUT =  self.IMAGE_OUTPUT + self.IMAGE_DATA + "-B_IMAGE-" + str(i) + "/"
		os.mkdir(self.IMAGE_OUTPUT)

	def process(self):
		
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
			"out" : self.IMAGE_OUTPUT + self.IMAGE_DATA + ".uvaver"
		})

		# Split channels
		cwd = os.getcwd()
		os.chdir(self.IMAGE_OUTPUT)
		maxwidth = input("Enter max imaging bandwidth per dataset (in Ghz i.e. 0.512): ")
		miriad_command(
		"uvsplit",
		{
			"vis" : self.IMAGE_OUTPUT + self.IMAGE_DATA + ".uvaver",
			"maxwidth" : maxwidth
		})
		os.chdir(cwd)

		# Output each of the created channels


# Advanced imaging class
class AIM():

	def __init__(self, settings):

		self.SETTINGS = settings

		print("Initialising advanced imaging")
		
		# Select calibration datasets
		calibration_selection = {}

		i = 0
		for f in os.listdir(settings["working_directory"]):
			calibration_selection[str(i)] = f
			i += 1

		print(calibration_selection)

		self.IMAGE_DATA = calibration_selection[ input("Enter selection of prepared imaging dataset: ") ]

	def process(self):
		pass