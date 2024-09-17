from werkzeug.security import generate_password_hash, check_password_hash
from IkonConveyancing.app import db
from flask_login import UserMixin
from flask import json
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from IkonConveyancing.app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    reminders = db.relationship('Reminder', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

# 
class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)  # New Title field
    subject = db.Column(db.String(150), nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subject': self.subject,
            'body': self.body,
            'user_id': self.user_id
        }


    def __repr__(self):
        return f"EmailTemplate('{self.subject}', '{self.user_id}')"
    def __repr__(self):
        return f"EmailTemplate('{self.subject}', '{self.client_name}')"

class ClientFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_number = db.Column(db.String(20), unique=False, nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    settlement_date = db.Column(db.Date, nullable=False)
    type_of_client = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    progress = db.Column(db.String(50), nullable=False)  # Progress bar value
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship with reminders
    reminders = db.relationship('Reminder', back_populates='client_file', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'file_number': self.file_number,
            'client_name': self.client_name,
            'settlement_date': self.settlement_date.isoformat(),
            'type_of_client': self.type_of_client,
            'progress': self.progress,
            'notes': self.notes
        }

    def to_dict(self):
        return {
            'id': self.id,
            'file_number': self.file_number,
            'client_name': self.client_name,
            'settlement_date': self.settlement_date.isoformat(),
            'type_of_client': self.type_of_client,
            'progress': self.progress,
            'notes': self.notes,
            'checklist_status': self.checklist_status
        }
class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_file_id = db.Column(db.Integer, db.ForeignKey('client_file.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'status': self.status
        }

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    priority = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'start': self.start.isoformat(),
            'description': self.description,
            'priority': self.priority,
            'user_id': self.user_id
        }


class TodoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'user_id': self.user_id
        }
# Reminder Model
class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reminder_text = db.Column(db.String(200), nullable=False)  # The reminder description
    reminder_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_completed = db.Column(db.Boolean, default=False)  # Marks whether the reminder is completed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_file_id = db.Column(db.Integer, db.ForeignKey('client_file.id'), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='reminders')  # Use back_populates instead of backref
    client_file = db.relationship('ClientFile', back_populates='reminders')  # Define the other side of the relationship

    def __repr__(self):
        return f'<Reminder {self.reminder_text}>'