from miriad import CALIBRATION_FLAGGING as M_CF
from miriad import menu

import json, os

main_menu = menu.menu("settings.json")

# Initialise settings
if (os.path.isfile(main_menu.SETTINGS_LOCATION)):
    with open(main_menu.SETTINGS_LOCATION, 'r') as f:
        settings = json.load(f)
else:
    settings = {
        "project_name" : "",
        "output_directory" : "",
        "working_directory" : ""
    }
    main_menu.update_settings()

# Main menu loop
main_menu.main_loop()