from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from IkonConveyancing.app import db
from IkonConveyancing.app.models import User, EmailTemplate
from flask_login import login_user, logout_user, login_required, current_user
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import jsonify
from datetime import datetime

@current_app.route('/')
def home():
    return render_template('index.html')

@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            return render_template('goodbyeworld.html')
        login_user(user)
        return render_template('helloworld.html')
    return render_template('login.html')

@current_app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html')

@current_app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@current_app.route('/client_files')
@login_required
def client_files():
    return render_template('client_files.html')

@current_app.route('/send_email')
@login_required
def send_email():
    return render_template('email.html')

@current_app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@current_app.route('/api/templates', methods=['GET', 'POST'])
@login_required
def manage_templates():
    if request.method == 'POST':
        data = request.json
        template = EmailTemplate(
            subject=data['subject'],
            settlement_date=data['settlement_date'],
            client_name=data['client_name'],
            address=data['address'],
            body=data['body'],
            user_id=current_user.id
        )
        db.session.add(template)
        db.session.commit()
        return jsonify({'message': 'Template created successfully'}), 201
    else:
        templates = EmailTemplate.query.filter_by(user_id=current_user.id).all()
        return jsonify([template.to_dict() for template in templates])

@current_app.route('/api/templates/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def update_delete_template(id):
    template = EmailTemplate.query.get_or_404(id)
    if request.method == 'PUT':
        data = request.json
        template.subject = data['subject']
        template.settlement_date = data['settlement_date']
        template.client_name = data['client_name']
        template.address = data['address']
        template.body = data['body']
        db.session.commit()
        return jsonify({'message': 'Template updated successfully'})
    elif request.method == 'DELETE':
        db.session.delete(template)
        db.session.commit()
        return jsonify({'message': 'Template deleted successfully'})

@current_app.route('/api/send_email', methods=['POST'])
@login_required
def send_email_api():
    data = request.json
    subject = data['subject']
    body = data['body']
    recipient = data['recipient']

    msg = MIMEMultipart()
    msg['From'] = 'your-email@gmail.com'
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('your-email@gmail.com', 'your-password')
        text = msg.as_string()
        server.sendmail('your-email@gmail.com', recipient, text)
        server.quit()
        return jsonify({'message': 'Email sent successfully'})
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@current_app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.username = request.form['username']
        current_user.email = request.form['email']
        if request.form['password']:
            current_user.set_password(request.form['password'])
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('profile'))
    return render_template('profile.html')
@current_app.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')

@current_app.route('/api/events', methods=['GET', 'POST'])
@login_required
def events():
    if request.method == 'POST':
        data = request.json
        event = Event(
            title=data['title'],
            start=datetime.fromisoformat(data['start']),
            description=data.get('description', ''),
            priority=data['priority'],
            user_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        return jsonify({'message': 'Event created successfully'}), 201
    else:
        date = request.args.get('date')
        if date:
            events = Event.query.filter(
                Event.user_id == current_user.id,
                Event.start.between(f"{date} 00:00:00", f"{date} 23:59:59")
            ).all()
        else:
            events = Event.query.filter_by(user_id=current_user.id).all()
        return jsonify([event.to_dict() for event in events])