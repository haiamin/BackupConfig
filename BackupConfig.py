#
# Title:	BackupConfig.py
# Author:	Niels Friis-Hansen
# Version:	1.0
#
# Revisions:	1.0	First draft version
#
# Descripion:
# Python script that backs up the configuration of Cisco IOS devices
#
# The script logs into each device for which login credentials are provided in the "devices.txt" file,
# lists the running and startup config and stores each in a separate file.
#

import csv
import re
from netmiko import ConnectHandler
from datetime import datetime
from time import strftime

# Define the names of files used
CSVDATA_FILENAME = 'devices.txt'

# Define list to hold config commands
config_cmds = []

# Record start-time
start_time = datetime.now()
start_time_text = start_time.strftime('%Y%m%d-%H%M%S')


# Define functions
def get_data(row):
	# Reads parameters from the CSV input-file
	data_fields = {
		field_name: field_value
		for field_name, field_value in row.items()
	}

# Main loop, log into each device for which credentials are included in the input CSV-file
for row in csv.DictReader(open(CSVDATA_FILENAME)):
    get_data(row)

	# Create a device object for input to netmikos ConnectHandler function
    device = {
        'device_type': row['DEVICETYPE'],
        'ip':   row['IP'],
        'username': row['USERNAME'],
        'password': row['PASSWORD'],
        'verbose': False,
    }

    # Connect to the device
    net_connect = ConnectHandler(**device)
	# ... and fetch the current running configuration into output
    output = net_connect.send_command("show run")

    # Read through the config and look for hostname, If found, store the name
    hostname = ""
    for line in output.split('\n'):
        matchObj = re.match( r'hostname (.+)', line)
        if matchObj:
            hostname = matchObj.group(1)
            print "Found hostname: ", matchObj.group(1), " in device with IP address", device['ip']

    filename = hostname + '_' + device['ip'] + "_" + start_time_text + '_running.txt'
    file = open(filename, 'w')
    file.write(output)
    file.close()

	# Fetch the current startup configuration into output
    output = net_connect.send_command("show start")

    filename = hostname + '_' + device['ip'] + "_" + start_time_text + '_startup.txt'
    file = open(filename, 'w')
    file.write(output)
    file.close()

    net_connect.disconnect()

end_time = datetime.now()

total_time = end_time - start_time
print "Total run time: ", total_time

