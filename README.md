# Apps get memory usage percentage export to CSV

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
### These classes are essential for interfacing with the Windows API to gather detailed information about system processes and their memory usage.
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
## SYSTEM_INFO
This class represents the SYSTEM_INFO structure in the Windows API, which contains information about the current computer system. This includes architecture, memory, and processor information.
```python
class SYSTEM_INFO(ctypes.Structure):
    _fields_ = [
        ("wProcessorArchitecture", ctypes.c_ushort),
        ("wReserved", ctypes.c_ushort),
        ("dwPageSize", ctypes.wintypes.DWORD),
        ("lpMinimumApplicationAddress", ctypes.wintypes.LPVOID),
        ("lpMaximumApplicationAddress", ctypes.wintypes.LPVOID),
        ("dwActiveProcessorMask", ctypes.c_size_t),  # Updated here
        ("dwNumberOfProcessors", ctypes.wintypes.DWORD),
        ("dwProcessorType", ctypes.wintypes.DWORD),
        ("dwAllocationGranularity", ctypes.wintypes.DWORD),
        ("wProcessorLevel", ctypes.c_ushort),
        ("wProcessorRevision", ctypes.c_ushort)
    ]
```
  - wProcessorArchitecture: The architecture of the processor (e.g., x86, x64).
  - wReserved: Reserved for future use.
  - dwPageSize: The page size and the granularity of page protection and commitment.
  - lpMinimumApplicationAddress: The lowest memory address accessible to applications and DLLs.
  - lpMaximumApplicationAddress: The highest memory address accessible to applications and DLLs.
  - dwActiveProcessorMask: A mask representing the set of processors configured into the system.
  - dwNumberOfProcessors: The number of logical processors in the current group.
  - dwProcessorType: An obsolete member, retained for compatibility.
  - dwAllocationGranularity: The granularity for the starting address at which virtual memory can be allocated.
  - wProcessorLevel: The architecture-dependent processor level.
  - wProcessorRevision: Architecture-dependent processor revision number.
## PROCESS_MEMORY_COUNTERS_EX
This class corresponds to the PROCESS_MEMORY_COUNTERS_EX structure provided by the Windows API, which provides information about the memory usage of a process.
```python
class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.wintypes.DWORD),
        ("PageFaultCount", ctypes.wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
        ("PrivateUsage", ctypes.c_size_t),
    ]
```
  - cb: The size of the structure, in bytes.
  - PageFaultCount: The number of page faults.
  - PeakWorkingSetSize: The peak working set size, in bytes.
  - WorkingSetSize: The current working set size, in bytes.
  - QuotaPeakPagedPoolUsage: The peak paged pool usage, in bytes.
  - QuotaPagedPoolUsage: The current paged pool usage, in bytes.
  - QuotaPeakNonPagedPoolUsage: The peak non-paged pool usage, in bytes.
  - QuotaNonPagedPoolUsage: The current non-paged pool usage, in bytes.
  - PagefileUsage: The Commit Charge value in bytes for this process.
  - PeakPagefileUsage: The peak value in bytes of the Commit Charge during the lifetime of this process.
  - PrivateUsage: The amount of memory that the process has allocated that cannot be shared with other processes, in
