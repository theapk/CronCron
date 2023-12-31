import json

from flask import Flask, request, jsonify, render_template
from bson import json_util
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime
import subprocess

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client['croncron']
users_collection = db['users']
collection = db['jobs']


def parse_json(data):
    return json.loads(json_util.dumps(data))


def is_process_running(process_name):
    try:
        output = subprocess.check_output('pgrep -fl ' + process_name, shell=True)
        if process_name in output.decode('utf-8'):
            return True
        else:
            return False
    except Exception as e:
        return False


@app.route('/', methods=['GET'])
def hello():
    return 'Hello, World!'


@app.route('/jobs/<job_id>', methods=['PUT'])
def update_job(job_id):
    print(f"job_id: {job_id}")
    job_id = ObjectId(job_id)
    job = collection.find_one({"_id": job_id})
    print(f"job: {job}")
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    job['last_run'] = request.json.get('last_run', job['last_run'])
    job['status'] = request.json.get('status', job['status'])
    collection.replace_one({'_id': job_id}, job)
    return jsonify({'message': 'Job updated'})


@app.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = collection.find()
    for job in jobs:
        print(f"jobs: {job}")
    results = [
        {
            'id': str(job['_id']),
            'name': job['name'],
            'user_id': job['user_id'],
            'name': job['name'],
            'command': job['command'],
            'schedule': job['schedule'],
            'last_run': job['last_run'],
            'status': job['status'],
            'output': job['output']
        } for job in jobs
    ]
    print(f"results: {results}")
    # res = json.dumps(results)
    # print(f"res: {res}")
    # print(f"res type: {type(res)}")
    return jsonify(results)


@app.route('/jobs/<user_id>', methods=['GET'])
def get_users_jobs(user_id):
    jobs = collection.find({"user_id": user_id})
    # for job in jobs:
    #     print(f"jobs: {job}")
    results = [{'id': str(job['_id']), 'user_id': job['user_id'], 'name': job['name'], 'command': job['command'],
                'schedule': job['schedule'],
                'last_run': job['last_run'], 'status': job['status']} for job in jobs]
    print(f"results: {results}")
    # res = json.dumps(results)
    # print(f"res: {res}")
    # print(f"res type: {type(res)}")
    return jsonify(results)


@app.route('/api/jobs', methods=['GET'])
def get_all_jobs():
    jobs = collection.find()
    return jsonify(
        [
            {
                '_id': str(job['_id']),
                'name': job['name'],
                'command': job['command'],
                'schedule': job['schedule'],
                'last_run': job['last_run'],
                'status': job['status'],
                'output': job['output'],
                'user_id': job['user_id']
            } for job in jobs
        ]
    )


@app.route('/dashboard', methods=['GET'])
def jobs():
    return render_template('dashboard.html')


@app.route('/jobs', methods=['POST'])
def create_job():
    res = request.json
    print(f"res: {res}")
    print(f"res type: {type(res)}")
    job = {
        '_id': res['job_id'],
        'command': res['command'],
        'schedule': res['schedule'],
        'user_id': res['user_id'],
        'last_run': res['last_run'],
        'status': res['status'],
        'name': res['name'],
        'output': res['output']
    }
    result = collection.insert_one(job)
    return jsonify({'id': str(result.inserted_id)})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8151)
