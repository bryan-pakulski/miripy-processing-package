from miriad import *

from miriad import CALIBRATION_FLAGGING as M_CF
from miriad import menu

# Initialise menu and load settings
main_menu = menu.menu("settings.json")

# Main menu loop
while (1):
    working_string = "(" + main_menu.SETTINGS['project_name'] + ") :: "
    choice = input("Settings (1) - Print working Dir (2) - Calibration (3) - Imaging (4) - Manual Command (5) - Exit (6)\n" + working_string)

    if (choice == "1"):
        main_menu.update_settings()

    elif (choice == "2"):
        os.system("ls " + main_menu.SETTINGS['working_directory'])

    elif (choice == "3"):
        pass

    elif (choice == "4"):
        pass

    elif (choice == "5"):
        cmd = main_menu.manual_command()
        miriad_command(cmd[0], cmd[1])

    elif (choice == "6"):
        break
    
    else:
        print("Invalid option...")