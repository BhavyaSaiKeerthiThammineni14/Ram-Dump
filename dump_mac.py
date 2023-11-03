import subprocess

# Get the PID of the process to dump
pid = input("Enter PID of process to dump: ")

# Define the filename and path for the dump file
dump_file = f"memdump_{pid}.core"

# Use gcore to create the memory dump
subprocess.run(["gcore", "-o", dump_file, pid], check=True)

print(f"Memory dump saved to {dump_file}")