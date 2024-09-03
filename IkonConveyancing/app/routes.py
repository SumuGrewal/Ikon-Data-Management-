from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from IkonConveyancing.app import db
from IkonConveyancing.app.models import User, EmailTemplate
from flask_login import login_user, logout_user, login_required, current_user
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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