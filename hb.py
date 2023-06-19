import os
import time
import requests
import subprocess
import argparse
from datetime import datetime

# Your Flask application URL
from bson import ObjectId

FLASK_APP_URL = 'http://localhost:8151/jobs'
OUTPUT_FILE_PATH = 'output.txt'  # Replace with the actual output file path

def is_process_running(process_name):
    try:
        split_process_name = process_name.split(' ')
        print(f"process_name: {split_process_name}")
        output = subprocess.check_output('pgrep -fl ' + process_name, shell=True)
        split_output = output.decode('utf-8').split(' ')
        print(f"output: {split_output}")
        if process_name in output.decode('utf-8'):
            return True
        else:
            return False
    except Exception as e:
        return False

def read_output_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def monitor_cron_jobs(cron_command, user_id):
    while True:
        # Fetch jobs from Flask app
        response = requests.get(FLASK_APP_URL)
        jobs = response.json()
        print(f"jobs: {jobs}")

        for job in jobs:
            if job['user_id'] != user_id:
                continue

            # Check if the job is running
            if is_process_running(cron_command):
                # If it is, update the last_run and status fields
                job['last_run'] = datetime.now().isoformat()
                job['status'] = 'running'
                job['output'] = read_output_file(OUTPUT_FILE_PATH)
                res = requests.put(f'{FLASK_APP_URL}/{job["id"]}', json=job)
                print(f"If Result: {res}")
            else:
                # If it's not, just update the status field
                print(f"ID: {job['id']['$oid']}")
                job['status'] = 'not running'
                full_path = f'{FLASK_APP_URL}/{job["id"]["$oid"]}'
                print(f"full_path: {full_path}")
                r = requests.put(full_path, json=job)
                print(f"Else Result: {r}")

        # Wait a while before checking again
        seconds = 10
        print(f"Sleeping for {seconds} seconds")
        time.sleep(seconds)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor a cron job.')
    parser.add_argument('command', type=str, help='The command of the cron job to monitor')
    parser.add_argument('user_id', type=str, help='The unique identifier of the user')
    args = parser.parse_args()

    monitor_cron_jobs(args.command, args.user_id)
