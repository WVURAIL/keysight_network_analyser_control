# keysight_network_analyser_control
Scripts to control and extract data from a Keysight Network Analyser

Currently only supports Windows

## Python dependencies

External packages used at time of documentation, newer version will mostly not break scripts.

```
matplotlib==3.3.4
numpy==1.19.2
PyVISA==1.11.3
scikit_rf==0.18.1
```

## Install VISA libraries 

Can be downloaded and installed from 
keysight  [here](https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html) 

or can install NI-VISA:
- Windows/macOS [here](https://pyvisa.readthedocs.io/en/latest/faq/getting_nivisa.html#faq-getting-nivisa)
- Linux [here](https://www.ni.com/en-us/support/downloads/drivers/download.ni-linux-device-drivers.html#409880) and instructions (here)[https://www.ni.com/en-us/support/documentation/supplemental/18/downloading-and-installing-ni-driver-software-on-linux-desktop.html] 

In the scripts edit  path to the appropraite library file

```
VISA_LIB_FILE_PATH = "C:\\Windows\\System32\\visa64.dll"
```
## Current scripts 

- `measure_s11.py`
- `measure_two_port_s_parameters.py`
- 
## Usage

Edit the parent directory where files and plots will be stored:
```
PARENT_DIR = "C:\\Users\\username\\Desktop\\workingdirectory\\"
```
Run script:
```
python ./measure_two_port_s_parameters
```

### TODO 
- linux support
