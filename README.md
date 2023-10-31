Short code-snippet to read the configuration of an Wago Modbus Coupler device (750-362, 750-89x,..)
in the main.py you'll find two parameters to set:
1. serverIP   -> that's the IP-Address of your Wago Coupler
2. outputFile -> this is the path where you will find the configuration of the scanned coupler in Json format

the Json files: 
Modules.json        -> this is the look-up table for all available modules from Wago (not Complete)
coupler_config.json -> this is the generated json config
