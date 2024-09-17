from flask import render_template, flash, redirect, url_for, request, current_app, jsonify, json
from IkonConveyancing.app import db
from IkonConveyancing.app.models import User, EmailTemplate, ClientFile, ChecklistItem, Event, TodoItem, Reminder
from flask_login import login_user, logout_user, login_required, current_user
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from twofactorauth import totp
import logging
import os
from werkzeug.utils import secure_filename

# Home route
@current_app.route('/')
def index():
    return render_template('index.html')

# Login route
@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user is None or not user.check_password(password):
            logging.debug(f"Invalid login attempt for email: {email}")
            return render_template('wrongpassword.html')

        # Redirect to 2FA instead of logging in immediately
        logging.debug(f"Password correct for user: {email}, redirecting to 2FA.")
        return redirect(url_for('two_factor_auth', user_id=user.id))
    
    return render_template('login.html')

# Two-factor authentication route
@current_app.route('/two_factor_auth/<int:user_id>', methods=['GET', 'POST'])
def two_factor_auth(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user_passcode = request.form['code']
        if totp.verify(str(user_passcode)):  # Ensure 2FA is valid
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid 2FA code', 'error')
    
    return render_template('two_factor_auth.html', user_id=user_id)

# Register route
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
        flash('You are now a registered user!')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Dashboard route
@current_app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Client files route
@current_app.route('/client_files')
@login_required
def client_files():
    return render_template('client_files.html')

# Send email route (view)
@current_app.route('/send_email')
@login_required
def send_email():
    return render_template('email.html')

# Logout route
@current_app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# API to manage email templates
@current_app.route('/api/templates', methods=['GET', 'POST'])
@login_required
def manage_templates():
    if request.method == 'POST':
        # Create a new template
        data = request.json
        new_template = EmailTemplate(
            title=data['title'],  # Ensure the title is captured
            subject=data['subject'],
            body=data['body'],
            user_id=current_user.id
        )
        db.session.add(new_template)
        db.session.commit()
        return jsonify(new_template.to_dict()), 201

    # Retrieve all templates for the logged-in user
    templates = EmailTemplate.query.filter_by(user_id=current_user.id).all()
    return jsonify([template.to_dict() for template in templates])

@current_app.route('/api/templates/<int:id>', methods=['PUT'])
@login_required
def update_template(id):
    template = EmailTemplate.query.get_or_404(id)
    data = request.json
    template.title = data['title']  # Ensure title is updated
    template.subject = data['subject']  # Ensure subject is updated
    template.body = data['body']  # Ensure body is updated
    db.session.commit()
    return jsonify(template.to_dict())

@current_app.route('/api/templates/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_single_template(id):
    template = EmailTemplate.query.get_or_404(id)

    if request.method == 'GET':
        # Return the template data
        return jsonify(template.to_dict())

    elif request.method == 'PUT':
        # Update an existing template
        data = request.json
        template.subject = data['subject']
        template.body = data['body']
        db.session.commit()
        return jsonify(template.to_dict())

    elif request.method == 'DELETE':
        # Delete the template
        db.session.delete(template)
        db.session.commit()
        return jsonify({'message': 'Template deleted successfully'})

# API to send emails
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

# Profile route
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

# Calendar view route
@current_app.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')

@current_app.route('/api/events', methods=['GET', 'POST'])
@login_required
def events():
    if request.method == 'POST':
        # Add a new event
        data = request.json
        new_event = Event(
            title=data['title'],
            start=datetime.fromisoformat(data['start']),
            description=data.get('description', ''),
            priority=data['priority'],
            user_id=current_user.id
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify({'message': 'Event created successfully'}), 201

    elif request.method == 'GET':
        # Get events by date, or return all events for the current user
        date = request.args.get('date')
        if date:
            events = Event.query.filter(
                Event.user_id == current_user.id,
                Event.start.between(f"{date} 00:00:00", f"{date} 23:59:59")
            ).all()
        else:
            events = Event.query.filter_by(user_id=current_user.id).all()

        return jsonify([event.to_dict() for event in events]), 200

# Checklist route
@current_app.route('/checklist')
@login_required
def checklist():
    return render_template('checklist.html')

# Client files API for adding/updating clients
@current_app.route('/api/client_files', methods=['POST', 'PUT'])
@login_required
def manage_client_files():
    try:
        client_name = request.form['clientName']
        email = request.form['email']
        contact_info = request.form['contact']
        address = request.form['address']
        settlement_date = request.form['settlementDate']
        type_of_client = request.form['typeOfClient']
        property_type = request.form['propertyType']
        notes = request.form['notes']

        # Handle document upload (if any)
        document = request.files['documents'] if 'documents' in request.files else None
        document_path = None
        if document:
            document_path = save_document(document)

        # Check if updating or adding new
        if request.method == 'PUT':
            client_id = request.form.get('clientId')
            client_file = ClientFile.query.get_or_404(client_id)
            client_file.client_name = client_name
            client_file.email = email
            client_file.contact_info = contact_info
            client_file.address = address
            client_file.settlement_date = datetime.strptime(settlement_date, '%Y-%m-%d').date()
            client_file.type_of_client = type_of_client
            client_file.property_type = property_type
            client_file.notes = notes
            if document_path:
                client_file.documents = document_path
        else:
            new_client_file = ClientFile(
                client_name=client_name,
                email=email,
                contact_info=contact_info,
                address=address,
                settlement_date=datetime.strptime(settlement_date, '%Y-%m-%d').date(),
                type_of_client=type_of_client,
                property_type=property_type,
                notes=notes,
                documents=document_path,
                user_id=current_user.id
            )
            db.session.add(new_client_file)

        db.session.commit()
        return jsonify(new_client_file.to_dict()), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400


# API for checklist
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
@current_app.route('/api/todos', methods=['GET', 'POST'])
@login_required
def manage_todos():
    if request.method == 'POST':
        data = request.json
        new_todo = TodoItem(
            description=data['description'],
            user_id=current_user.id
        )
        db.session.add(new_todo)
        db.session.commit()
        return jsonify(new_todo.to_dict()), 201
    
    todos = TodoItem.query.filter_by(user_id=current_user.id).all()
    return jsonify([todo.to_dict() for todo in todos])

@current_app.route('/api/todos/<int:id>', methods=['DELETE'])
@login_required
def delete_todo_item(id):
    todo = TodoItem.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'To-do item deleted successfully'})
@current_app.route('/api/client_files', methods=['POST'])
@login_required
def add_client_file():
    data = request.json
    new_file = ClientFile(
        file_number=data['fileNumber'],
        settlement_date=datetime.strptime(data['settlementDate'], '%Y-%m-%d').date(),
        user_id=current_user.id
    )
    db.session.add(new_file)
    db.session.commit()
    return jsonify(new_file.to_dict()), 201
# Save checklist progress for a specific file
@current_app.route('/api/save_checklist/<file_number>', methods=['POST'])
@login_required
def save_checklist(file_number):
    data = request.json
    checklist_status = data['checklistStatus']

    # Find the file and update its checklist status (store it as JSON in the database)
    client_file = ClientFile.query.filter_by(file_number=file_number, user_id=current_user.id).first_or_404()
    client_file.checklist_status = json.dumps(checklist_status)
    db.session.commit()

    return jsonify({'message': 'Checklist progress saved successfully'}), 200


# Load checklist for a specific file
@current_app.route('/api/load_checklist/<file_number>', methods=['GET'])
@login_required
def load_checklist(file_number):
    client_file = ClientFile.query.filter_by(file_number=file_number, user_id=current_user.id).first_or_404()
    if client_file.checklist_status:
        checklist_status = json.loads(client_file.checklist_status)
    else:
        checklist_status = {}  # Return empty if no checklist has been saved

    return jsonify({'checklistStatus': checklist_status}), 200
# API to delete an event
@current_app.route('/api/events/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403

    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted successfully'}), 200
@current_app.route('/api/get_urgent_reminders', methods=['GET'])
@login_required
def get_urgent_reminders():
    urgent_reminders = Reminder.query.filter(
        Reminder.reminder_datetime <= datetime.now(),
        Reminder.user_id == current_user.id
    ).all()

    # Prepare data to send as JSON
    reminder_list = [{
        'id': reminder.id,
        'reminder_text': reminder.reminder_text,
        'reminder_datetime': reminder.reminder_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        'client_file': reminder.client_file.client_name  # Assuming Reminder is linked to ClientFile
    } for reminder in urgent_reminders]

    return jsonify(reminder_list)

# Define where to save uploaded documents
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx', 'txt'}

# Make sure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """ Check if the file extension is allowed """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_document(document):
    """ Save the document to the uploads folder """
    if document and allowed_file(document.filename):
        filename = secure_filename(document.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        document.save(file_path)  # Save the file
        return file_path
    else:
        raise ValueError("File type not allowed")