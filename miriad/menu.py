class menu():

    def __init__(self, settings):
        print("Initialised main menu")
        self.SETTINGS_LOCATION = settings
    
    def update_settings(self):
        pass

    # Capture input and run miriad command
    def main_input(self):
        while (1):
            input("Input phase")
