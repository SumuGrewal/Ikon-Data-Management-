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