############################################
# @Purpose:Measure_S11.py: A script designed to test Chime feed antennas for S11. The script walks you through
# testing of antennas and saves files and graphs locally.
#
# @Authors: Pranav Sanghavi and Joseph Shepard
#
# @Date: 9/13/2021
###############################################

import os

import numpy as np
import skrf as rf
import matplotlib.pyplot as plt
import time
import pyvisa as visa
import time

import vna_control as vna
from vna_control import (check_power_mode, measure_s_parameter,
                         set_freq_lims, set_power_mode)



    # ```
    # For NA Mode:
    # Reverse measurements are available ONLY with full S-parameter option.
    #
    # S11 - Forward reflection measurement
    # S21 - Forward transmission measurement
    # S12 - Reverse transmission
    # S22 - Reverse reflection
    # A - A receiver measurement
    # B - B receiver measurement
    # R1 - Port 1 reference receiver measurement
    # R2 - Port 2 reference receiver measurement
    # ```


def execute_measurement(start_freq, stop_freq):
    KEEP_MEASURING = True
    while KEEP_MEASURING:
        con = input(
            "Please Connect the VNA and ensure it is powered on! Once connected press y: ")
        if con == 'y':
            vna.intialize_network_analyzer(VISA_LIB_FILE_PATH)
        ##########################################################################
        # set start and stop freq
            set_freq_lims(start_freq, stop_freq)
        ##########################################################################

            serial_num = input("Please Enter Antenna Serial Number: ")
            z = input("Please Connect VNA to P1! Press Enter when Finished: ")
            serial_num_1 = serial_num+"_P1"
            m = "S11"
            output_power = "HIGH"
            S11, S11_raw = measure_s_parameter(
                m, serial_num_1, start_freq, stop_freq, output_power, nominal_power=-15, plot=False)

            f = np.linspace(start_freq, stop_freq, S11_raw.shape[-1])
            nw2 = rf.Network(name=f"{serial_num_1}",
                             s=S11_raw, frequency=f, z0=50)
            print(nw2)
            nw2.write_touchstone(
                filename=f"{serial_num_1}", dir=f"{TOUCHSTONE_DIR}")

        # plot a smith chart of s11
            nw2.plot_s_smith()
            plt.title(f"{serial_num_1} Smith Chart")
            plt.savefig(
                os.path.join(SMITH_PLOT_DIR, f"{serial_num_1}.jpg"))

            print("Please Connect VNA to P2!")
            z = input("Please Connect VNA to P2!Press enter when Finished: ")
            serial_num_2 = serial_num+"_P2"
            m = "S11"
            output_power = "HIGH"
            S11, S11_raw = measure_s_parameter(
                m, serial_num_2, start_freq, stop_freq, output_power,
                nominal_power=-15, plot=False)

            f = np.linspace(start_freq, stop_freq, S11_raw.shape[-1])
            nw2 = rf.Network(name=f"{serial_num_2}",
                             s=S11_raw, frequency=f, z0=50)
            print(nw2)
            nw2.write_touchstone(
                filename=f"{serial_num_2}", dir=f"{TOUCHSTONE_DIR}")

        # plot a smith chart of s11
            nw2.plot_s_smith()
            plt.title(f"{serial_num_2} Smith Chart")
            plt.savefig(
                os.path.join(SMITH_PLOT_DIR, f"{serial_num_2}.jpg"))

        i = input("Finished? Press 0. Test another antenna? Press 1 : ")
        if i == '1':
            KEEP_MEASURING = True
        else:
            KEEP_MEASURING = False
    print("Measurement Done!")


if __name__ == "__main__":
    # TODO : add argument parsers
    start_freq = 1e7
    stop_freq = 2e9
    
    if start_freq > stop_freq:
        print("start frequency is greater than stop freq. fix and rerun")
        exit()
       
    VISA_LIB_FILE_PATH = "C:\\Windows\\System32\\visa64.dll"
    PARENT_DIR = "C:\\Users\\RadioLab\\Desktop\\Testing\\"

    PLOT_DIR = PARENT_DIR + "S11_Plots\\"

    vna.PLOT_DIR = PLOT_DIR
    TOUCHSTONE_DIR = PARENT_DIR + "Touchstone_Files"
    SMITH_PLOT_DIR = PARENT_DIR + "Smith_Charts\\"

    # create appropriate dirs
    if not os.path.exists(PLOT_DIR):
        os.makedirs(PLOT_DIR)
    if not os.path.exists(TOUCHSTONE_DIR):
        os.makedirs(TOUCHSTONE_DIR)
    if not os.path.exists(SMITH_PLOT_DIR):
        os.makedirs(SMITH_PLOT_DIR)

    execute_measurement(start_freq, stop_freq)
