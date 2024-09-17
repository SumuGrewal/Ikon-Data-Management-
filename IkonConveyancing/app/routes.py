from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from IkonConveyancing.app import db
from IkonConveyancing.app.models import User, EmailTemplate, ClientFile, ChecklistItem, Event, TodoItem
from flask_login import login_user, logout_user, login_required, current_user
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from twofactorauth import totp
import logging
import os

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
            subject=data['subject'],
            body=data['body'],
            user_id=current_user.id
        )
        db.session.add(new_template)
        db.session.commit()
        return jsonify({'message': 'Template created successfully'}), 201
    
    # Retrieve all templates for the logged-in user
    templates = EmailTemplate.query.filter_by(user_id=current_user.id).all()
    return jsonify([template.to_dict() for template in templates])

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
        return jsonify({'message': 'Template updated successfully'})

    elif request.method == 'DELETE':
        # Delete the template
        db.session.delete(template)
        db.session.commit()
        return jsonify({'message': 'Template deleted successfully'})
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

# API for calendar events
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

    elif request.method == 'GET':
        date = request.args.get('date')
        if date:
            events = Event.query.filter(
                Event.user_id == current_user.id,
                Event.start.between(f"{date} 00:00:00", f"{date} 23:59:59")
            ).all()
            return jsonify([event.to_dict() for event in events]), 200
        else:
            return jsonify({'message': 'Date parameter is missing'}), 400

# Checklist route
@current_app.route('/checklist')
@login_required
def checklist():
    return render_template('checklist.html')

# API for client files
@current_app.route('/api/client_files', methods=['GET', 'POST'])
@login_required
def manage_client_files():
    if request.method == 'POST':
        try:
            file_number = request.form['fileNumber']
            client_name = request.form['clientName']
            settlement_date = request.form['settlementDate']
            type_of_client = request.form['typeOfClient']
            progress = request.form['progress']
            notes = request.form['notes']

            if not all([file_number, client_name, settlement_date, type_of_client, progress]):
                return jsonify({'error': 'Missing required fields'}), 400

            new_client_file = ClientFile(
                file_number=file_number,
                client_name=client_name,
                settlement_date=datetime.strptime(settlement_date, '%Y-%m-%d').date(),
                type_of_client=type_of_client,
                progress=progress,
                notes=notes
            )
            db.session.add(new_client_file)
            db.session.commit()
            return jsonify(new_client_file.to_dict()), 201
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    else:
        files = ClientFile.query.all()
        return jsonify([file.to_dict() for file in files])

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
