from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import Job
import subprocess

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    command = db.Column(db.String(120), nullable=False)
    schedule = db.Column(db.String(120), nullable=False)
    last_run = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=True)

def is_process_running(process_name):
    try:
        output = subprocess.check_output('pgrep -fl ' + process_name, shell=True)
        if process_name in output.decode('utf-8'):
            return True
        else:
            return False
    except Exception as e:
        return False


@app.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = Job.query.all()
    return jsonify([{'name': job.name, 'command': job.command, 'schedule': job.schedule, 'last_run': job.last_run, 'status': job.status} for job in jobs])

@app.route('/jobs', methods=['POST'])
def create_job():
    job = Job(name=request.json['name'], command=request.json['command'], schedule=request.json['schedule'])
    db.session.add(job)
    db.session.commit()
    return jsonify({'id': job.id})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
