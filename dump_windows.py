import os
import psutil
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, sys.argv[0], None, 1)
    sys.exit()
    
# Get the directory of the Python interpreter or the executable file
current_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

dump_folder_path = os.path.abspath(os.path.join(current_dir, "memory_dumps"))

if not os.path.exists(dump_folder_path):
    os.mkdir(dump_folder_path)


for proc in psutil.process_iter(['pid', 'name']):
    process_name = proc.info['name']
    pid = proc.info['pid']

    process_handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
    if process_handle:
        print(f"Dumping memory of process {process_name} with pid {pid}...")
        memory_info = psutil.Process(pid).memory_info()
        start_address = memory_info.rss
        end_address = start_address + memory_info.vms
        memory_dump = ctypes.create_string_buffer(end_address - start_address)
        bytes_read = ctypes.c_size_t(0)
        ctypes.windll.kernel32.ReadProcessMemory(process_handle, start_address, memory_dump, end_address - start_address, ctypes.byref(bytes_read))
        dump_file_path = os.path.join(dump_folder_path, f"{process_name}_{pid}.dmp")
        dump_file_handle = ctypes.windll.kernel32.CreateFileW(dump_file_path, 0x10000000, 0, None, 2, 0x80, None)
        if dump_file_handle != -1:
            written = ctypes.c_ulong(0)
            ctypes.windll.kernel32.WriteFile(dump_file_handle, memory_dump, len(memory_dump), ctypes.byref(written), None)
            ctypes.windll.kernel32.CloseHandle(dump_file_handle)
            print(f"Memory dump saved to {dump_file_path}")
        else:
            print(f"Could not create file {dump_file_path}")
    else:
        print(f"Could not open process {process_name} with pid {pid}")
