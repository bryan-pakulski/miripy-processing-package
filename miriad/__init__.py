import subprocess

# Performs a basic miriad command
def miriad_command(command, parameters):
	options = []

	options.append(command)

	for key in parameters.keys():
		options.append(key + "=" + parameters[key])

	print("Running miriad command: ", options)
	subprocess.call(options)