#!/usr/bin/python3
import json
import time
import requests
import subprocess
import argparse
from datetime import datetime

# Your Flask application URL

FLASK_APP_URL = 'https://croncron.com/jobs'
OUTPUT_FILE_PATH = 'output.txt'  # Replace with the actual output file path


def is_process_running(process_name):
    try:
        split_process_name = process_name.split(' ')
        print(f"process_name: {split_process_name}")
        output = subprocess.check_output('pgrep -fl ' + split_process_name[1], shell=True)
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


def monitor_cron_jobs(cron_command, job_id, user_id):
    r = requests.get(FLASK_APP_URL + f"/{job_id}")
    print(f"r: {r}")

    while True:
        # Fetch jobs from Flask app
        response = requests.get(FLASK_APP_URL)
        jobs = response.json()
        print(f"jobs: {jobs}")

        # Find job with specified job_id
        job = next((job for job in jobs if job['id'] == job_id), None)

        if job is None:
            # If job does not exist, create new job
            job = {
                '_id': job_id,
                'command': cron_command,
                'user_id': user_id,
                'status': 'not running',
                'last_run': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            response = requests.post(FLASK_APP_URL, json=job)
            print(f"New job created: {response}")
            # job['id'] = response.json()['id']
            print(f"New job created: {job}")

        # Check if the job is running
        if is_process_running(cron_command):
            # If it is, update the last_run, output and status fields
            job['last_run'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            job['status'] = 'running'
            job['output'] = read_output_file(OUTPUT_FILE_PATH)
        else:
            # If it's not, just update the last_run and status field
            job['status'] = 'not running'
            job['last_run'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update job
        response = requests.put(f'{FLASK_APP_URL}/{job_id}', json=job)
        print(f"Update Result: {response}")

        # Wait a while before checking again
        seconds = 10
        print(f"Sleeping for {seconds} seconds")
        time.sleep(seconds)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor a cron job.')
    parser.add_argument('command', type=str, help='The command of the cron job to monitor')
    parser.add_argument('job_id', type=str, help='The unique identifier of the Cron job')
    parser.add_argument('user_id', type=str, help='The unique identifier of the user')
    args = parser.parse_args()

    monitor_cron_jobs(args.command, args.job_id, args.user_id)
