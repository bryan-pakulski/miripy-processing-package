import os, json

class menu():

    def __init__(self, setting_location):
        print("Initialised main menu")
        self.SETTINGS_LOCATION = setting_location

        # Initialise settings
        if (os.path.isfile(self.SETTINGS_LOCATION)):
            with open(self.SETTINGS_LOCATION, 'r') as f:
                self.SETTINGS = json.load(f)
        else:
            self.SETTINGS = {
                "project_name" : "",
                "working_directory" : ""
            }
            self.update_settings()
            self.save_settings()

    def save_settings(self):
        with open(self.SETTINGS_LOCATION, 'w') as f:
                json.dump(self.SETTINGS, f)

    
    def update_settings(self):
        selection = ""
        
        while (selection != "1" and selection != "2"):
            selection = input("Create new project (1) - Select Project (2)\n:: ")
        
        # Create new project
        if (selection == "1"):
            project_name = input("Enter project code/name: ")
            wrk_dir = input("Enter project folder location: ")
        
            # Create folder with project code
            output_dir = wrk_dir + "/" + project_name + "/"
            os.mkdir(output_dir)

            # Update settings and save to file
            self.SETTINGS["project_name"] = project_name
            self.SETTINGS["working_directory"] = output_dir
        
        # Select a different project
        else:
            project_name = input("Enter project name: ")
            wrk_dir = input("Enter project location: ")

            self.SETTINGS["project_name"] = project_name
            self.SETTINGS["working_directory"] = wrk_dir
            self.save_settings()

    def print_working_dir(self):
        pass

    def calibration(self):
        pass

    def imaging(self):
        pass
    
    # Returns command and options to pass through to miriad
    def manual_command(self):

        cmd = input("Enter miriad command: ")

        options = {}
        capture = ""
        
        while (capture != "qqq"):
            op = input("Enter option / (qqq) to cancel: ")

            if (op == "qqq"):
                break
            else:
                val = input("Enter " + op + " value: ")

            options[op] = val

        return (cmd, options)