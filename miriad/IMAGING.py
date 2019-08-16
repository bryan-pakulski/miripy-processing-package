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
		region = ""

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
		
		return region

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
						self.IMAGE_MAP = self.IMAGE_CHOICE + ".mp"
						self.IMAGE_BEAM = self.IMAGE_CHOICE + ".bm"
						self.IMAGE_MODEL = self.IMAGE_CHOICE + ".md"
						self.IMAGE_RESTOR = self.IMAGE_CHOICE + ".rst"
						self.IMAGE_RESIDUAL = self.IMAGE_CHOICE + ".rsd"

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
				"range" : "0,0,log,0",
				"options" : "grid,wedge"
			})

			# Visualise data, returns img coordinates for imfit
			region = self.image()

			# Measure flux density
			print("Measuring flux density of source")
			obj = input("Select object type (level, gaussian, disk, point, beam): ")
			miriad_command(
			"imfit",
			{
				"in" : self.IMAGE_RESTOR,
				"region" : region,
				"object" : obj,
				"spar" : "1,0,0",
				"out" : self.IMAGE_RESIDUAL,
				"options" : "residual"
			})

			# Display distribution of flux
			input("Press <Enter> to measure flux distribution: ")
			miriad_command(
			"imhist",
			{
				"in" : self.IMAGE_RESIDUAL,
				"region": region,
				"options" : "nbin,100",
				"device" : "/xs"
			})



# Advanced imaging class
class AIM():

	def __init__(self, settings):

		self.SETTINGS = settings
		self.IMAGE_OUTPUT = self.SETTINGS["working_directory"]

		print("Initialising advanced imaging")
		print("Please make sure to have completed basic imaging on the target before performing this function")
		
		# Select calibration datasets
		calibration_selection = {}

		i = 0
		for f in os.listdir(settings["working_directory"]):
			calibration_selection[str(i)] = f
			i += 1

		print(calibration_selection)

		self.IMAGE_OUTPUT =  self.IMAGE_OUTPUT + calibration_selection[ input("Enter selection of imaging output_folder (BIMG-X): ") ]

	# Display image
	def cgdisp(self, image, region, col):
		miriad_command(
		"cgdisp",
		{
			"in" : image,
			"type" : "p",
			"region" : region,
			"device" : "/xs",
			"labtyp" : "hms,dms",
			"range" : "0,0,log," + col,
			"options" : "wedge, unequal"
		})

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

						self.IMAGE_MAP = self.IMAGE_CHOICE + ".mp"
						self.IMAGE_BEAM = self.IMAGE_CHOICE + ".bm"
						self.IMAGE_MODEL = self.IMAGE_CHOICE + ".md"
						self.IMAGE_RESTOR = self.IMAGE_CHOICE + ".rst"
						self.IMAGE_RESIDUAL = self.IMAGE_CHOICE + ".rsd"

						#### OLD DATA FROM BASIC IMAGING ####
						self.IMAGE_BASIC_RESTOR = self.IMAGE_CHOICE + ".rst"
						self.IMAGE_BASIC_RESIDUAL = self.IMAGE_CHOICE + ".rsd"

						#### NEW DATA FROM ADVANCED IMAGING #####
						self.IMAGE_ADVANCED_MAP = self.IMAGE_CHOICE + ".Amp"
						self.IMAGE_ADVANCED_BEAM = self.IMAGE_CHOICE + ".Abm"
						self.IMAGE_ADVANCED_MODEL = self.IMAGE_CHOICE + ".Amd"
						self.IMAGE_ADVANCED_RESTOR = self.IMAGE_CHOICE + ".Arst"
						self.IMAGE_ADVANCED_RESIDUAL = self.IMAGE_CHOICE + ".Arsd"

			except QUIT:
				break

			# Determine size of image made with imlist
			print("Determining size of imlist image in pixels")
			miriad_command(
			"imlist",
			{
				"in" : self.IMAGE_BASIC_RESTOR,
				"options" : "statistics"
			})

			# Determine pixel size
			print("Determening absolute pixel / arc references")
			miriad_command(
			"impos",
			{
				"in" : self.IMAGE_BASIC_RESTOR,
				"coord" : "1,1",
				"type" : "abspix"
			})

			print("Please enter image information from above output...")

			ix = float(input("Enter image X Size: "))
			iy = float(input("Enter image Y Size: "))
			px = float(input("Enter pixel X reference: "))
			py = float(input("Enter pixel Y reference: "))
			ax = float(input("Enter ARC X reference: "))
			ay = float(input("Enter ARC Y reference: "))

			# Perform invert to make image with a 3x size beam
			miriad_command(
			"invert",
			{
				"vis" : self.IMAGE_CHOICE,
				"map" : self.IMAGE_ADVANCED_MAP,
				"beam" : self.IMAGE_ADVANCED_BEAM,
				"imsize" : str(ix*3) + "," + str(iy*3),
				"cell" : str(ax/px) + "," + str(ay/py),
				"sup" : "0",
				"stokes" : "i",
				"options" : "mfs,sdb"
			})

			# Look at dirty map
			print("Displaying dirty map")
			self.cgdisp(self.IMAGE_ADVANCED_MAP, "", "")

			# Clean image
			print("Deconvolving image...")
			cutoff = input("Enter absoluate cutoff value for amplitude (i.e. 4e-5): ")
			niters = input("Enter n iterations: ")
			miriad_command(
			"mfclean",
			{
				"map" : self.IMAGE_ADVANCED_MAP,
				"beam" : self.IMAGE_ADVANCED_BEAM,
				"out" : self.IMAGE_ADVANCED_MODEL,
				"cutoff" : cutoff,
				"niters" : niters,
				"region" : "relcenter,boxes(-%f,-%f,%f,%f)" % (px, py, px, py)
			})

			# Create image from model
			miriad_command(
			"restor",
			{
				"model" : self.IMAGE_ADVANCED_MODEL,
				"beam" : self.IMAGE_ADVANCED_BEAM,
				"map" : self.IMAGE_ADVANCED_MAP,
				"out" : self.IMAGE_ADVANCED_RESTOR
			})

			# Preview cleaned image
			print("Previewing cleaned image")
			self.cgdisp(self.IMAGE_ADVANCED_RESTOR, "", "")

			# Measure flux density
			print("Measuring flux density of source")
			miriad_command(
			"imfit",
			{
				"in" : self.IMAGE_ADVANCED_RESTOR,
				"object" : "point",
				"spar" : "1,0,0",
				"out" : self.IMAGE_ADVANCED_RESIDUAL,
				"options" : "residual"
			})

			# Display distribution of flux
			input("Press <Enter> to measure flux distribution: ")
			miriad_command(
			"imhist",
			{
				"in" : self.IMAGE_ADVANCED_RESIDUAL,
				"region": "relcenter,boxes(-11,-16,18,13)",
				"options" : "nbin,100",
				"device" : "/xs"
			})