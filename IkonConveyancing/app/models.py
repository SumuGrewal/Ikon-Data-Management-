from werkzeug.security import generate_password_hash, check_password_hash
from IkonConveyancing.app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(150), nullable=False)
    settlement_date = db.Column(db.String(150), nullable=False)
    client_name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(150), nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'settlement_date': self.settlement_date,
            'client_name': self.client_name,
            'address': self.address,
            'body': self.body,
            'user_id': self.user_id
        }

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
    progress = db.Column(db.String(50), nullable=False)  # Add this line

    def to_dict(self):
        return {
            'id': self.id,
            'file_number': self.file_number,
            'client_name': self.client_name,
            'settlement_date': self.settlement_date.isoformat(),
            'type_of_client': self.type_of_client,
            'progress': self.progress,  # Add this line to the dict
            'notes': self.notes
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
