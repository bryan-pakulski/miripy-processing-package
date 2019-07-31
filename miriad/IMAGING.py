from . import *
from . import FLAGGING

# Exception class for nested while escape
class QUIT( Exception ): pass

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

		self.IMAGE_OUTPUT =  self.IMAGE_OUTPUT + calibration_selection[ input("Enter selection of imaging output_folder (BIMG-X): ") ]

	def process(self):
		
		while(1):
			
			# Select frequency to image
			image_choice = ""
			
			i = 0
			image_selection = {}
			for f in os.listdir(self.IMAGE_OUTPUT):
				image_selection[str(i)] = f
				i += 1

			print(image_selection)

			try:
				while (image_choice == ""):
					image_choice = input("Enter frequency range to image, qqq to quit: ")

					if (image_choice == "qqq"):
						raise QUIT
					else:
						self.IMAGE_CHOICE = self.IMAGE_OUTPUT + "/" + image_selection[image_choice] 
						self.IMAGE_MAP = self.IMAGE_CHOICE + ".imap"
						self.IMAGE_BEAM = self.IMAGE_CHOICE + ".ibeam"
						self.IMAGE_MODEL = self.IMAGE_CHOICE + ".imodel"
						self.IMAGE_RESTOR = self.IMAGE_CHOICE + ".irestor"

			except QUIT:
				break

			# Create dirty map / dirty synthesized beam
			print("Creating dirty map/beam for frequency: " + image_choice)
			robust = input("Enter a robust value between -2 (Sensitivity) and 2 (Resolution): ")
			miriad_command(
			"invert",
			{
				"vis" : self.IMAGE_CHOICE,
				"map" : self.IMAGE_MAP,
				"beam" : self.IMAGE_BEAM,
				"robust" : robust,
				"stokes" : "i",
				"options" : "mfs,double"
			})

			# Create preview of dirty map
			print("Previewing dirty map")
			miriad_command(
			"cgdisp",
			{
				"in" : self.IMAGE_MAP,
				"type" : "p",
				"device" : "/xs",
				"labtyp" : "hms,dms",
				"options" : "wedge"
			})
			input("Press Enter to continue")

			# Clean image
			print("Cleaning image")
			cutoff = input("Enter cutoff for abs value of amplitude (i.e. 5e-5): ")
			niters = input("Number of iterations: ")
			miriad_command(
			"clean",
			{
				"map" : self.IMAGE_MAP,
				"beam" : self.IMAGE_BEAM,
				"out" : self.IMAGE_MODEL,
				"options" : "negstop,positive",
				"cutoff" : cutoff,
				"niters" : niters
			})

			# Create image from model
			miriad_command(
			"restor",
			{
				"model" : self.IMAGE_MODEL,
				"beam" : self.IMAGE_BEAM,
				"map" : self.IMAGE_MAP,
				"out" : self.IMAGE_RESTOR
			})

			# Display newly cleaned image
			print("Previewing cleaned image")
			miriad_command(
			"cgdisp",
			{
				"in" : self.IMAGE_RESTOR,
				"type" : "p",
				"device" : "/xs",
				"labtyp" : "hms,dms",
				"range" : "0,0,log",
				"options" : "wedge"
			})
			input("")



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