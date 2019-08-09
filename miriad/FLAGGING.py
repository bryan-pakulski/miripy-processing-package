from . import *

class FLAGGING():

	def __init__():
		pass

	# Basic RFI flagging steps for calibration
	def basic_flagging(self, vis_source):

		# Flag RFI
		miriad_command(
		"pgflag",
		{
			"vis" : vis_source,
			"stokes" : "xx,yy",
			"device" : "/xs",
			"command" : "<b",
			"options" : "nodisp"
		})

		miriad_command(
		"pgflag",
		{
			"vis" : vis_source,
			"stokes" : "yy,xx",
			"device" : "/xs",
			"command" : "<b",
			"options" : "nodisp"
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