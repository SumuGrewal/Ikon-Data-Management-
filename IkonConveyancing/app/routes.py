from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from IkonConveyancing.app import db
from IkonConveyancing.app.models import User, EmailTemplate, ClientFile, ChecklistItem
from flask_login import login_user, logout_user, login_required, current_user
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from twofactorauth import totp
import logging
import os
from .models import Event

@current_app.route('/')
def index():
    return render_template('index.html')

@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user is None:
            logging.debug(f"User with email {email} not found.")
            return render_template('wrongpassword.html')
        
        if not user.check_password(password):
            logging.debug(f"Password for user with email {email} is incorrect.")
            return render_template('wrongpassword.html')
        
        # Instead of logging in the user here, redirect to the 2FA page
        logging.debug(f"User with email {email} found and password is correct. Redirecting to 2FA.")
        return redirect(url_for('two_factor_auth', user_id=user.id))
    
    return render_template('login.html')

@current_app.route('/two_factor_auth/<int:user_id>', methods=['GET', 'POST'])
def two_factor_auth(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user_passcode = request.form['code']
        if totp.verify(str(user_passcode)):  # Implement this function to verify the 2FA code
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid 2FA code', 'error')
    return render_template('two_factor_auth.html', user_id=user_id)

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

@current_app.route('/api/templates', methods=['GET','POST'])
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
        # Ensure 'start' is correctly formatted and all required fields are present
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

    elif request.method == 'GET':
        # Handle getting events by date, e.g., filtering by a specific day
        date = request.args.get('date')
        if date:
            events = Event.query.filter(
                Event.user_id == current_user.id,
                Event.start.between(f"{date} 00:00:00", f"{date} 23:59:59")
            ).all()

            # Use the to_dict method you defined to serialize events
            events_data = [event.to_dict() for event in events]
            return jsonify(events_data), 200
        else:
            return jsonify({'message': 'Date parameter is missing'}), 400

@current_app.route('/checklist')
@login_required
def checklist():
    return render_template('checklist.html')

@current_app.route('/api/client_files', methods=['GET'])
@login_required
def get_client_files():
    files = ClientFile.query.all()
    return jsonify([file.to_dict() for file in files])

@current_app.route('/api/checklist/<int:file_id>', methods=['GET'])
@login_required
def get_checklist(file_id):
    checklist_items = ChecklistItem.query.filter_by(client_file_id=file_id).all()
    return jsonify([item.to_dict() for item in checklist_items])

@current_app.route('/api/checklist/<int:item_id>', methods=['PUT'])
@login_required
def update_checklist_item(item_id):
    item = ChecklistItem.query.get_or_404(item_id)
    data = request.json
    item.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Checklist item updated successfully'})

@current_app.route('/api/checklist/<int:file_id>/progress', methods=['GET'])
@login_required
def get_checklist_progress(file_id):
    checklist_items = ChecklistItem.query.filter_by(client_file_id=file_id).all()
    total_items = len(checklist_items)
    completed_items = sum(1 for item in checklist_items if item.status == 'completed')
    progress = (completed_items / total_items) * 100 if total_items > 0 else 0
    return jsonify({'progress': progress})

@current_app.route('/client_files/<file_number>')
@login_required
def client_details(file_number):
    client_file = ClientFile.query.filter_by(file_number=file_number).first_or_404()
    return render_template('client_details.html', client_file=client_file)

@current_app.route('/api/client_files', methods=['POST'])
@login_required
def add_client_file():
    data = request.json
    file_number = data.get('file_number')
    logging.debug(f"Received file_number: {file_number}")
    
    if not file_number:
        logging.debug("File number is missing in the request.")
        return jsonify({'message': 'File number is required'}), 400
    
    existing_file = ClientFile.query.filter_by(file_number=file_number).first()
    
    if existing_file:
        logging.debug(f"File number {file_number} already exists in the database.")
        return jsonify({'message': f'File number {file_number} already exists'}), 400

    try:
        settlement_date = datetime.strptime(data['settlement_date'], '%Y-%m-%d').date()
        new_file = ClientFile(
            file_number=['file_number'],
            client_name=data['client_name'],
            address=data['address'],
            status=data['status'],
            settlement_date=settlement_date,
            type_of_settlement=data['type_of_settlement'],
            type_of_client=data['type_of_client'],
            notes=data.get('notes')
        )
        db.session.add(new_file)
        db.session.commit()
        logging.debug(f"Client file with file_number {file_number} added successfully.")
        return jsonify({'message': 'Client file added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding client file: {str(e)}")
        return jsonify({'message': str(e)}), 500

@current_app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        file_number = request.form['fileNumber']
        filename = f"{file_number}_{file.filename}"
        file_path = os.path.join(current_app.root_path, filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200

@current_app.route('/api/client_files/<int:id>', methods=['PUT'])
@login_required
def update_client_file(id):
    data = request.json
    client_file = ClientFile.query.get_or_404(id)
    
    client_file.file_number = data['file_number']
    client_file.client_name = data['client_name']
    client_file.address = data['address']
    client_file.status = data['status']
    client_file.settlement_date = datetime.strptime(data['settlement_date'], '%Y-%m-%d').date()
    client_file.type_of_settlement = data['type_of_settlement']
    client_file.type_of_client = data['type_of_client']
    client_file.notes = data.get('notes', client_file.notes)
    
    db.session.commit()
    return jsonify({'message': 'Client file updated successfully'})