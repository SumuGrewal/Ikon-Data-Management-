from flask import render_template, flash, redirect, url_for, request, current_app
from IkonConveyancing.app import db
from IkonConveyancing.app.models import User

@current_app.route('/')
def home():
    return render_template('index.html')

@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(f"Login attempt with email: {email} and password: {password}")  # Debug print statement
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            print("Login failed: Invalid email or password")  # Debug print statement
            return render_template('goodbye.html')
        print("Login successful")  # Debug print statement
        return render_template('hello.html')
    return render_template('login.html')

@current_app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Debug print statements
        print(f"Registering user with Username: {username}, Email: {email}, Password: {password}")
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print("User registered successfully")  # Debug print statement
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html')