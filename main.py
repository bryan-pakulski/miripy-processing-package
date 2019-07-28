from miriad import *

from miriad import CALIBRATION_FLAGGING as M_CF
from miriad import IMAGING as IM
from miriad import menu

# Initialise menu and load settings
main_menu = menu.menu("settings.json")

# Main menu loop
while (1):
	working_string = "(" + main_menu.SETTINGS['project_name'] + ") :: "
	choice = input("(1) Settings - (2) Print working Dir - (3) Calibration - (4) Imaging- (5) Manual Command - (6) Exit \n" + working_string)

	if (choice == "1"):
		main_menu.update_settings()

	elif (choice == "2"):
		os.system("ls " + main_menu.SETTINGS['working_directory'])

	elif (choice == "3"):
		
		fc = ""

		while (fc != "0" and fc != "1"):
			fc = input("(0) Begin Basic Calibration or (1) Advanced Calibration: ")
		
		if (fc == "0"):
			cf = M_CF.BCF(main_menu.SETTINGS)
		else:
			cf = M_CD.ACF(main_menu.SETTINGS)

		cf.process()
	
	elif (choice == "4"):

		fc = ""

		while (fc != "0" and fc != "1"):
			fc = input("(0) Begin Basic Calibration or (1) Advanced Calibration: ")
		
		if (fc == "0"):
			im = IM.BIM(main_menu.SETTINGS)
		else:
			im = IM.AIM(main_menu.SETTINGS)

		im.process()

	elif (choice == "5"):
		cmd = main_menu.manual_command()
		miriad_command(cmd[0], cmd[1])

	elif (choice == "6"):
		break
	
	else:
		print("Invalid option...")