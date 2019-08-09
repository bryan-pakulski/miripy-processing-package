from . import *
from . import FLAGGING
import curses

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
	
	# Display image
	def cgdisp(self, region, col):
		miriad_command(
		"cgdisp",
		{
			"in" : self.IMAGE_RESTOR,
			"type" : "p",
			"region" : region,
			"device" : "/xs",
			"labtyp" : "hms,dms",
			"range" : "0,0,log," + col,
			"options" : "wedge"
		})

	# Visualisation modes
	def image(self):
		# Image sub areas
		while (1):

			im = input("Select subregion to image (0) Yes Manual - (1) Yes Interactive - (2) No: ")
			
			# Exit sub imaging
			if (im == "2"):
				break
			
			# Interactive imaging
			if (im == "1"):

				img_size = int(input("Select image size (500): "))
				inc = int(input("Select increment size (50): "))
				col = input("select color display (miriad -> cgdisp -> range): ")

				region_x1 = 0
				region_y1 = 0
				region_x2 = img_size
				region_y2 = img_size

				region = "boxes(%i,%i,%i,%i)" % (region_x1, region_y1, region_x2, region_y2)

				self.cgdisp(region, col)

				print("Entering interactive mode, arrows keys to navigate, q to exit")

				screen = curses.initscr()
				curses.noecho()
				curses.cbreak()
				screen.keypad(True)

				while (1):
					
					direction = screen.getch()
					if direction == ord('q'): 
						break

					elif direction == curses.KEY_UP:
						region_y1 += inc
						region_y2 += inc

					elif direction == curses.KEY_DOWN:
						region_y1 -= inc
						region_y2 -= inc

					elif direction == curses.KEY_RIGHT:
						region_x1 += inc
						region_x2 += inc

					elif direction == curses.KEY_LEFT:
						region_x1 -= inc
						region_x2 -= inc

					# Boundary definitions
					if region_x1 < 0:
						region_x1 = 0
					if region_x2 < 0:
						region_x2 = 0
					if region_y1 < 0:
						region_y1 = 0
					if region_y2 < 0:
						region_y1 = 0

					region = "boxes(%i,%i,%i,%i)" % (region_x1, region_y1, region_x2, region_y2)
					self.cgdisp(region, col)
				
				# shut curses down cleanly
				curses.nocbreak()
				screen.keypad(0)
				curses.echo()
				curses.endwin()

			# Manual region selection		
			if (im == "0"):
				region_x1 = input("Enter region x1: ")
				region_y1 = input("Enter region y1: ")
				region_x2 = input("Enter region x2: ")
				region_y2 = input("Enter region y2: ")

				region = "boxes(%i,%i,%i,%i)" % (region_x1, region_y1, region_x2, region_y2)

				col = input("select color display (miriad -> cgdisp -> range): ")
				self.cgdisp(region, col)
			

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
						self.IMAGE_RESIDUAL = self.IMAGE_CHOICE + ".iresidual"

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
				"imsize" : "3,3,beam",
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
				"region" : "images",
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
				"region" : "images",
				"device" : "/xs",
				"labtyp" : "hms,dms",
				"range" : "0,0,log,2",
				"options" : "grid,wedge"
			})

			# Visualise data
			self.image()

			# Measure flux density
			print("Measuring flux density of source")
			miriad_command(
			"imfit",
			{
				"in" : self.IMAGE_RESTOR,
				"region" : "quarter",
				"object" : "point",
				"spar" : "1,0,0",
				"out" : self.IMAGE_RESIDUAL,
				"options" : "residual"
			})



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