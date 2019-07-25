import os, json

from . import *

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


    # Initialise miriad project, create UV object, flag RFI, split channels
    def initialise_project(self, input_file):
        
        # Load data
        miriad_command(
        "atlod",
        {
            "in" : input_file,
            "out" : self.SETTINGS["working_directory"] + self.SETTINGS["project_name"] + ".uv",
            "ifsel" : "1",
            "options" : "birdie,rfiflag,noauto,xycorr"
        })

        # Flag RFI
        edge = input("Enter edge value for RFI flagging, see miriad help on uvflag for more info: ")
        miriad_command(
        "uvflag",
        {
            "vis" : self.SETTINGS["project_name"] + ".uv",
            "edge" : edge,
            "flagval" : "flag"
        })

        # Split channels
        cwd = os.getcwd()
        os.chdir(self.SETTINGS["working_directory"])
        miriad_command(
        "uvsplit",
        {
            "vis" : self.SETTINGS["project_name"] + ".uv"
        })
        os.chdir(cwd)
    

    def update_settings(self):
        selection = ""
        
        while (selection != "1" and selection != "2"):
            selection = input("Create new project (1) - Select Project (2)\n:: ")
        
        # Create new project
        if (selection == "1"):
            project_name = input("Enter project code/name: ")
            wrk_dir = input("Enter project folder location: ")
        
            # Create folder with project code
            output_dir = wrk_dir + project_name + "/"
            os.mkdir(output_dir)

            # Update settings and save to file
            self.SETTINGS["project_name"] = project_name
            self.SETTINGS["working_directory"] = output_dir

            input_file = input("Enter path of input dataset: ")

            self.initialise_project(input_file)
        
        # Select a different project
        else:
            project_name = input("Enter project name: ")
            wrk_dir = input("Enter project location: ")

            self.SETTINGS["project_name"] = project_name
            self.SETTINGS["working_directory"] = wrk_dir
            self.save_settings()


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