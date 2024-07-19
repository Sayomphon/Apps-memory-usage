# Apps-memory-usage

This code is a Python script that monitors the memory usage of a list of predefined applications on a Windows system. 
It periodically retrieves the memory usage of each running instance of a monitored application and saves this data, along with a timestamp, to a CSV file. 
The script creates a new folder and CSV file every 30 seconds to keep the data organized. The monitored applications are defined in the apps_to_monitor list. 
To collect memory usage data, the script uses the ctypes library to call Windows API functions. The script runs until the user interrupts it with Ctrl+C.

## Imports and Constants
  - ctypes: A foreign function library for Python, allowing calling functions in DLLs or shared libraries.
  - time: Provides various time-related functions.
  - csv: To handle CSV file reading and writing.
  - os: Provides a way to use operating system-dependent functionality like reading or writing to the file system.
```python
import ctypes
import ctypes.wintypes
import time
import csv
import os
import subprocess
```
## Constants and Type Definitions
These constants are used to define the access permissions for reading process memory and querying process information.
```python
# Define the necessary constants and types
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MAX_PATH = 260
```
## PROCESSENTRY32
This class corresponds to the PROCESSENTRY32 structure provided by the Windows API, which is used to store information about processes in the system.
```python
class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.wintypes.DWORD),
        ("cntUsage", ctypes.wintypes.DWORD),
        ("th32ProcessID", ctypes.wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.wintypes.ULONG)),
        ("th32ModuleID", ctypes.wintypes.DWORD),
        ("cntThreads", ctypes.wintypes.DWORD),
        ("th32ParentProcessID", ctypes.wintypes.DWORD),
        ("pcPriClassBase", ctypes.wintypes.LONG),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("szExeFile", ctypes.c_char * MAX_PATH)
    ]
```
  - dwSize: Size of the structure, in bytes. This field should be initialized to sizeof(PROCESSENTRY32).
  - cntUsage: The number of references to the process.
  - th32ProcessID: The identifier of the process.
  - th32DefaultHeapID: A pointer to the process's default heap.
  - th32ModuleID: The identifier of the module associated with the process.
  - cntThreads: The number of execution threads started by the process.
  - th32ParentProcessID: The identifier of the parent process.
  - pcPriClassBase: The base priority of any threads created by this process.
  - dwFlags: Flags that represent process state information.
  - szExeFile: The name of the executable file for the process, limited to MAX_PATH characters.
