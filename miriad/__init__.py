import os, sys

# Performs a basic miriad command
def miriad_command(command, parameters):
	cmd = command + " "

	for key in parameters.keys():
		cmd += key + "=" + parameters[key] + " "

	print("Running miriad command: ", cmd)
	os.system(cmd)