# Apps-memory-usage

This code is a Python script that monitors the memory usage of a list of predefined applications on a Windows system. 
It periodically retrieves the memory usage of each running instance of a monitored application and saves this data, along with a timestamp, to a CSV file. 
The script creates a new folder and CSV file every 30 seconds to keep the data organized. The monitored applications are defined in the apps_to_monitor list. 
To collect memory usage data, the script uses the ctypes library to call Windows API functions. The script runs until the user interrupts it with Ctrl+C.
