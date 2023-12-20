import ctypes
import ctypes.wintypes
import time
import csv
import os

# Define the necessary constants and types
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MAX_PATH = 260

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

# Get memory usage function
def get_process_memory_usage(process_id):
    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi

    process_handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, process_id)

    process_memory_counters = PROCESS_MEMORY_COUNTERS_EX()
    process_memory_counters.cb = ctypes.sizeof(process_memory_counters)
    if psapi.GetProcessMemoryInfo(process_handle, ctypes.byref(process_memory_counters), ctypes.sizeof(process_memory_counters)):
        # Dereference the pointer and access the value
        private_usage = process_memory_counters.PrivateUsage
        return private_usage

    kernel32.CloseHandle(process_handle)

# Get running apps function    
def get_running_apps():
    # Create a snapshot of the running processes
    snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
    if snapshot == -1:
        return []

    # Retrieve the information of each process in the snapshot
    process_entry = PROCESSENTRY32()
    process_entry.dwSize = ctypes.sizeof(process_entry)
    if not ctypes.windll.kernel32.Process32First(snapshot, ctypes.byref(process_entry)):
        ctypes.windll.kernel32.CloseHandle(snapshot)
        return []

    apps = []
    while True:
        app_name = process_entry.szExeFile.decode()
        if app_name in apps_to_monitor:
            apps.append((process_entry.th32ProcessID, app_name))

        if not ctypes.windll.kernel32.Process32Next(snapshot, ctypes.byref(process_entry)):
            break

    ctypes.windll.kernel32.CloseHandle(snapshot)
    return apps

# Create folder to save files function
def create_folder(path):
    folder_name = time.strftime("%Y-%m-%d_%H-%M-%S")
    folder_path = os.path.join(path, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    print("Data will be saved in the following folder:")
    print(folder_path)
    return folder_path

# Apps to monitors
apps_to_monitor = ["Your_app 1", "Your_app 2", "Your_app n"]

# Get the current script path
script_path = os.path.dirname(os.path.abspath(__file__))

# Set the initial timestamp and folder path
current_time = time.time()
folder_path = create_folder(script_path)
folder_data = {folder_path: {app_name: [] for app_name in apps_to_monitor}}
next_folder_time = current_time + 30  # Create the first folder after 30 seconds

try:
    while True:
        current_time = time.time()

        # Check if it's time to create a new folder
        if current_time >= next_folder_time:
            folder_path = create_folder(script_path)
            folder_data[folder_path] = {app_name: [] for app_name in apps_to_monitor}
            next_folder_time = current_time + 30  # Update the next folder creation time

        # Get the current timestamp
        current_time = time.localtime()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
        day = time.strftime("%Y-%m-%d", current_time)
        time_only = time.strftime("%H:%M:%S", current_time)

        running_apps = get_running_apps()

        # Collect the memory usage data for each app
        for process_id, app_name in running_apps:
            if app_name in apps_to_monitor:
                memory_usage = get_process_memory_usage(process_id)
                if memory_usage is not None:
                    folder_data[folder_path][app_name].append([day, time_only, memory_usage])

        # Wait for 4 seconds before the next iteration
        time.sleep(4)
        
except KeyboardInterrupt:  # Stop the code with Ctrl+C
    # Write data to separate CSV files for each folder and app
    for folder_path, folder_app_data in folder_data.items():
        for app_name, app_data in folder_app_data.items():
            csv_filename = os.path.join(folder_path, "{}.csv".format(app_name))
            with open(csv_filename, "w", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["Day", "Time", "CTC process", "Memory Usage (KB)"])  # Add "App Name" to the header

                # Write the data for each app
                for data_row in app_data:
                    day, time_only, memory_usage = data_row
                    csv_writer.writerow([day, time_only, app_name, memory_usage])

    print("\nMonitoring stopped by user.")