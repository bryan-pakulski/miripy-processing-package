from miriad import *

from miriad import CALIBRATION_FLAGGING as M_CF
from miriad import menu

# Initialise menu and load settings
main_menu = menu.menu("settings.json")

# Main menu loop
while (1):
    working_string = "(" + main_menu.SETTINGS['project_name'] + ") :: "
    choice = input("Settings (1) - Print working Dir (2) - Calibration/Imaging (3) Manual Command (4) - Exit (5)\n" + working_string)

    if (choice == "1"):
        main_menu.update_settings()

    elif (choice == "2"):
        os.system("ls " + main_menu.SETTINGS['working_directory'])

    elif (choice == "3"):
        
        fc = ""

        while (fc != "0" and fc != "1"):
            fc = input("Begin Basic Calibration (0) or Advanced Calibration (1): ")
        
        if (fc == "0"):
            cf = M_CF.BCF(main_menu.SETTINGS)
        else:
            cf = M_CD.ACF(main_menu.SETTINGS)


    elif (choice == "5"):
        cmd = main_menu.manual_command()
        miriad_command(cmd[0], cmd[1])

    elif (choice == "6"):
        break
    
    else:
        print("Invalid option...")