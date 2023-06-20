import subprocess

# Get the process IDs of running Gunicorn instances
command = "pgrep -f 'gunicorn'"
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, _ = process.communicate()

if process.returncode == 0:
    process_ids = output.decode().strip().split('\n')

    print("Running Gunicorn processes:")
    for process_id in process_ids:
        # Retrieve the command line arguments of each Gunicorn process
        command = f"ps -p {process_id} -o command --no-header"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = process.communicate()
        command_line = output.decode().strip()

        print(f"Process ID: {process_id}")
        print(f"Command line: {command_line}")
        print()
else:
    print("No running Gunicorn processes found.")
