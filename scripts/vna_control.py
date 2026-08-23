"""
Shared control functions for the Keysight network analyser.

These were duplicated verbatim across measure_s11.py and
measure_two_port_s_paramters.py. The four SCPI helpers had byte-identical
abstract syntax trees in both copies, so this module is a move rather than a
rewrite -- the source text is unchanged apart from the visa_lib argument noted
below.

State lives here on purpose. intialize_network_analyzer() assigns the module
level VNA object that the other functions write SCPI commands to, and
measure_s_parameter() saves plots into PLOT_DIR. A calling script sets
PLOT_DIR before measuring:

    import vna_control as vna
    vna.PLOT_DIR = PLOT_DIR
    vna.intialize_network_analyzer()

intialize_network_analyzer() takes an optional visa_lib path. Passing one
selects an explicit VISA library, as Windows sometimes needs; passing nothing
lets PyVISA find it, which is what the two-port script already did.

The intialize_ spelling is a typo, kept because callers outside this repository
may already use it.
"""

import time

import matplotlib.pyplot as plt
import numpy as np
import pyvisa as visa
import skrf as rf

# Set by intialize_network_analyzer(); every other function writes to it.
VNA = None

# Where measure_s_parameter() saves plots. Callers override this.
PLOT_DIR = "."




def set_freq_lims(start, stop):
    """
    set_freq_lims [Set frequency limits of measurement]
    [GP-IB Commands:
    http://na.support.keysight.com/pna/help/latest/Programming/GP-IB_Command_Finder/Sense/Frequency.htm]
    Parameters
    ----------
    start : [float]
        [in Hz]
    stop : [fload]
        [in Hz]
    """
    VNA.write('SENSe:FREQuency:STARt ' + str(start))
    VNA.write('SENSe:FREQuency:STOp ' + str(stop))


def check_power_mode():
    """
    CHECK POWER MODE
    """
    print(f"Current Output power is {VNA.query('SOURce:POWer:ALC:MODE?')}")


def set_power_mode(output_power, nominal_power=-15):
    """
    set_power_mode [set power level for your measurement]
    [set power, can be "HIGH", "LOW" or "MAN" if "MAN" ie manual set `nominal power`]
    Parameters
    ----------
    output_power : [str]
        ["HIGH", "LOW" or "MAN"]
    nominal_power : int, optional
        [description], by default -15dB
        Source power/attenuator level.
        N9912A: 0 to -31 dB in 1 dB steps
        N9923A: 0 to -47 dB in .5 dB steps
        All other models: Set power level from +3 to -45 dBm in .1 dB steps.
    """
    print(f"Setting output power to {output_power}")
    VNA.write('SOURce:POWer:ALC:MODE ' + str(output_power))
    check_power_mode()
    if str(output_power) == "MAN":
        print(f"Setting nominal power/attenuation level {nominal_power}")
        VNA.write('SOURce:POWer ' + str(nominal_power))


def measure_s_parameter(measurement, serial_num, start_freq, stop_freq, output_power, nominal_power=-15, plot=False):
    """
    measure_s_parameter [measures S parameter of choice]
    [S11, S12, S21, S22, for given power level. ]
    Parameters
    ----------
    measurement :[str]]
        ["S11", "S12", "S21", "S22"]
    serial_num : [str]
        [ID of device being measured]
    start_freq : [float]
        [in Hz]
    stop_freq : [float]
        [in Hz]
    output_power : [str]
        ["HIGH", "LOW" or "MAN"]
    nominal_power : [float]
        [in dB]
    Returns
    -------
    [tuple of nd.array]
        [(data, data_raw) where data is the log magnitude and the data_raw is the complex measurement]
    """
    print("setting frequency limits")
    set_freq_lims(start_freq, stop_freq)
    check_power_mode()

    set_power_mode(output_power, nominal_power)
    print(f"Measuring {measurement} with Output mode {output_power}")
    VNA.write(':CALCulate:PARameter1:DEFine ' + measurement)
    # http://na.support.keysight.com/pna/help/latest/Programming/GP-IB_Command_Finder/Calculate/Parameter.htm COMMANDS FOR MEASUREMENT PARAMETERS
    VNA.write(':CALCulate:SELected:FORMat MLOGarithmic')
    # MLINear, MLOGarithmic, PHASe, UPHase 'Unwrapped phase, IMAGinary,REAL
    # POLar SMITh, SADMittance 'Smith Admittance, SWR, GDELay 'Group Delay
    # http://na.support.keysight.com/pna/help/latest/Programming/GP-IB_Command_Finder/Calculate/Format_Calc.htm
    time.sleep(1)
    # scaling plot on the VNA screen
    VNA.write(':DISPlay:WINDow:TRACe:Y:SCALe:AUTO')
    # OTHER VNA COMMANDS THAT CONTROL THE SCREEN
    # http://na.support.keysight.com/pna/help/latest/Programming/GP-IB_Command_Finder/Display.htm#yauto
    ##########
    data = VNA.query('CALCulate:DATA:FDaTa?')
    # http://na.support.keysight.com/pna/help/latest/Programming/GP-IB_Command_Finder/Calculate/Data.htm # COMMANDS TO SAVE DATA
    data = data_real = np.asarray(data.split(
        ',')[:-1] + [data.split(',')[-1][:-1]])
    data = np.array([float(i.lower()) for i in data])
    print(f"DONE measuring {measurement}")

    if plot:
        plt.figure()
        plt.plot(np.linspace(start_freq/1e6,
                             stop_freq/1e6, data.shape[-1]), data)
        plt.xlabel("MHz")
        plt.ylabel("dBm")
        plt.title(f"{measurement}_{serial_num}")
        plt.show()
        plt.savefig(
            f"{PLOT_DIR}{measurement}_{serial_num}.png")

    VNA.write(':CALCulate:SELected:FORMat REAL')
    time.sleep(1)
    data_real = VNA.query('CALCulate:DATA:FDaTa?')
    data_real = np.asarray(data_real.split(
        ',')[:-1] + [data_real.split(',')[-1][:-1]])
    VNA.write(':CALCulate:SELected:FORMat IMAG')
    time.sleep(1)
    data_imag = VNA.query('CALCulate:DATA:FDaTa?')
    data_imag = np.asarray(data_imag.split(
        ',')[:-1] + [data_imag.split(',')[-1][:-1]])
    data_raw = np.array([float(i[0].lower())+float(i[1].lower())
                         * 1j for i in zip(data_real, data_imag)])
    return data, data_raw


def intialize_network_analyzer(visa_lib=None):
    global VNA
    ##############################################################################
    # load visa library
    rm = visa.ResourceManager(visa_lib) if visa_lib else visa.ResourceManager()
    #rm = visa.ResourceManager(VISA_LIB_FILE_PATH)  # windows
    # TODO linux
    # https://edadocs.software.keysight.com/kkbopen/linux-io-libraries-faq-589309025.html
    # https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html click linux
    #
    # find connected instrument and get instrument address
    print(rm.list_resources())
    instrument_address = rm.list_resources()[0]
    # load  instrument object
    VNA = rm.open_resource(instrument_address)
    VNA.write('*IDN?')
    IDN = VNA.read()
    print(IDN)
    VNA.timeout = 10000
    # # select NA mode
    # ```
    # Relevant Modes
    #  ALL
    #
    # Parameters
    #
    #
    # <string>
    #  Operating Mode. Case-sensitive. Choose from the modes that are installed on your FieldFox:
    #
    # "CAT"
    # "IQ"
    # "NA"
    # "SA"
    # "Power Meter"
    # "VVM"
    # "Pulse Measurements"
    # "ERTA"
    #
    # Examples
    #  INST "NA";*OPC?
    #  ```
    #
    # common commands: http://na.support.keysight.com/pna/help/latest/Programming/GP-IB_Command_Finder/Common_Commands.htm

    # print available modes of instrument
    print(VNA.query('INSTrument:CATalog?'))

    VNA.write('INST "NA";*OPC?')  # set in network analyzer mode

    if VNA.read()[0] == '1':
        print("Successfully set NA mode")
