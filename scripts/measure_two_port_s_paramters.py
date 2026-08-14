############################################
# @Purpose:measure_two_port_s_paramters.py: A script measure 2 port S parameters. can easily be extended.
#
# @Authors: Pranav Sanghavi and Joseph Shepard
#
# @Date: 9/13/2021
###############################################

import numpy as np
import skrf as rf
import matplotlib.pyplot as plt
import time
import pyvisa as visa
import time
import os
from sys import exit

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
    """
    execute_measurement [Get two port S parameters from the network analyzer]
    [saves touchstone files in TOUCHSTONE_DIR]
    Parameters
    ----------
    start_freq : [float]
        [in Hz]
    stop_freq : [float]
        [in Hz]
    """
    KEEP_MEASURING = True
    while KEEP_MEASURING:
        con = input(
            "Please Connect the VNAs and ensure it is powered on! Once connected press y: ")
        if con == 'y':
            vna.intialize_network_analyzer()

        ##########################################################################
        # set start and stop freq
            set_freq_lims(start_freq, stop_freq)
        ##########################################################################

            serial_num = input("Please Enter Device Serial Number: ")
            z = input("Please Connect VNA to Device! Press Enter when Finished: ")
            serial_num_1 = serial_num

            output_power = "LOW"
            #nominal_power=-15
            m = "S11"
            S11, S11_raw = measure_s_parameter(
                m, serial_num_1, start_freq, stop_freq, output_power, nominal_power=-15, plot=False)
            output_power = "LOW"
            #nominal_power=-15
            m = "S12"
            S12, S12_raw = measure_s_parameter(
                m, serial_num_1, start_freq, stop_freq, output_power, nominal_power=-15, plot=False)
            output_power = "LOW"
            #nominal_power=-15
            m = "S21"
            S21, S21_raw = measure_s_parameter(
                m, serial_num_1, start_freq, stop_freq, output_power, nominal_power=-15, plot=False)
            output_power = "LOW"
            #nominal_power=-15
            m = "S22"
            S22, S22_raw = measure_s_parameter(
                m, serial_num_1, start_freq, stop_freq, output_power, nominal_power=-15, plot=False)

            f = np.linspace(start_freq, stop_freq, S11_raw.shape[-1])

            s = np.zeros((len(f), 2, 2))+1.0j
            s[:, 0, 0] = S11_raw
            s[:, 0, 1] = S12_raw
            s[:, 1, 0] = S21_raw
            s[:, 1, 1] = S22_raw

            nw = rf.Network(name=f"{serial_num_1}", s=s, frequency=f, z0=50)
            nw.write_touchstone(
                filename=f"{serial_num_1}", dir=f"{TOUCHSTONE_DIR}")
            #nw.plot_s_db(label=f"{serial_num_1}")
            #plt.show()
            #plt.savefig(f"{PLOT_DIR}{serial_num}.png")
        i = input("Finished? Press 0. Test another Device? Press 1 : ")
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

    PLOT_DIR = PARENT_DIR + "S_Plots\\"

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
