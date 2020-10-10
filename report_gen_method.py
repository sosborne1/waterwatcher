#!/usr/bin/python3

import io         # used to create file streams
from io import open

import time       # used for sleep delay and timestamps
import string     # helps parse strings
from i2c import AtlasI2C

import os         # used to create folders
from pathlib import Path    #used to ignore warning of duplicate folders
from os.path import join as pjoin       #used to move files into folder

import pathlib     # used for creating multiple directories

def report_generator(address=None):
    device = AtlasI2C()     # creates the I2C port object, specify the address or bus if necessary
    num_of_readings = 3
    upper_tol_ph = 8.0
    lower_tol_ph = 7.2
    upper_tol_orp = 900
    lower_tol_orp = 600
    delay_time = 3
    avg_orp_reading = None
    avg_ph_reading = None

    #Get the current time to use for the filename
    now = time.strftime("%d-%b-%Y-%H%M%S")
    file_name = "Report_" + now
    year = time.strftime("%Y")
    month = time.strftime("%B")
    time_path = "Reports/" + year + '/' + month
    #creates folders and checks for duplicates
    p = pathlib.Path(time_path)
    p.mkdir(parents=True, exist_ok=True)
    ph_sensor_okay = True
    orp_sensor_okay = True
        
    #moves files into folder
    path_to_file = pjoin(time_path, file_name)
    file = open(path_to_file + '.txt', "w+")

    file.write(str("--------------------------------------------------------------------------"))
    file.write(str("\n\t\t\tReport for " + now))
    if(address is not None):
        file.write(str("\n\t\t\t" + address))
    try:
        #Set the address for pH sensor
        device.set_i2c_address(99)

        readings = []
        # Get readings of data on pH sensor
        for i in range(num_of_readings):
            sensor_query = device.query("R")
            sensor_query  = sensor_query.replace('\x00', '')
            #query_list = sensor_query.split()
            readings.append(float(sensor_query))
            time.sleep(delay_time - AtlasI2C.long_timeout)

        # Get average of those readings
        avg_ph_reading = round(sum(readings) / len(readings),2)

        # Check if the average is within bounds
        if avg_ph_reading >= lower_tol_ph and avg_ph_reading <= upper_tol_ph:
            file.write(str("\n\npH reading passes with value " + str(avg_ph_reading) + '\n'))
        else:
            file.write(str("\n!!!!!!!! pH reading fails with value " + str(avg_ph_reading) + "!!!!!!!!\n"))
        file.write(str("Tolerances are Min: " + str(lower_tol_ph) + " Max: " + str(upper_tol_ph) + '\n\n'))
    except IOError:
        file.write(str("\n!!!!!!!! PH SENSOR DISCONNECTED !!!!!!!\n\n"))
        ph_sensor_okay = False

    # Do same for ORP sensor
    # Change address for orp sensor
    try:
        device.set_i2c_address(98)

        readings = []
        for i in range(num_of_readings):
            sensor_query = device.query("R")
            sensor_query  = sensor_query.replace('\x00', '')
            #query_list = sensor_query.split()
            readings.append(float(sensor_query))
            time.sleep(delay_time - AtlasI2C.long_timeout)

        # Get average of those readings
        avg_orp_reading = round(sum(readings) / len(readings),2)

        # Check if the average is whithin bounds
        if avg_orp_reading >= lower_tol_orp and avg_orp_reading <= upper_tol_orp:
            file.write(str("ORP reading passes with value " + str(avg_orp_reading) + '\n'))
        else:
            file.write(str("\n!!!!!!!! ORP reading fails with value " + str(avg_orp_reading) + "!!!!!!!!\n"))
        file.write(str("Tolerances are Min: " + str(lower_tol_orp) + " Max: " + str(upper_tol_orp) + '\n\n'))
        file.write(str("--------------------------------------------------------------------------\n\n"))
    except IOError:
        file.write(str("\n!!!!!!!! ORP SENSOR DISCONNECTED !!!!!!!\n\n\n"))
        orp_sensor_okay = False

    file.close()

    # Write the the terminal what is in the text file
    #print(open(path_to_file + '.txt', 'r').read())
    
    return avg_orp_reading, avg_ph_reading, orp_sensor_okay, ph_sensor_okay




if __name__ == '__main__':
    report_generator()

