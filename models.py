from app import db

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    command = db.Column(db.String(120), nullable=False)
    schedule = db.Column(db.String(120), nullable=False)
    last_run = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=True)
