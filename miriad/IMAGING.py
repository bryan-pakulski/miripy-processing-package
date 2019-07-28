from . import *

# Basic imaging class
class BIM():

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

		self.IMAGE_DATA = calibration_selection[ input("Enter selection of imaging dataset: ") ]

		# Create subfolder for imaging, increment ID by + 1 if another folder exists
		i = 0
		while os.path.exists(self.IMAGE_DATA+"-B_IMAGE-%s" % i):
			i += 1
		
		self.IMAGE_OUTPUT = self.SETTINGS["working_directory"] + self.IMAGE_DATA + "-B_IMAGE-" + str(i) + "/"
		os.mkdir(self.IMAGE_OUTPUT)

	def process():
		pass

# Advanced imaging class
class AIM():

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

		self.IMAGE_DATA = calibration_selection[ input("Enter selection of prepared imaging dataset: ") ]

	def process():
		pass