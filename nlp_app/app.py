import os
from flask import Flask, jsonify, render_template,redirect, url_for, flash, session, request
from db import Database
from routes.nlp_routes import nlp_bp
import requests

APP_NAME = "TextChar AI"

# creater flask instance/object
app = Flask(__name__) # main file 
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key') # secret key for session management
app.register_blueprint(nlp_bp, url_prefix='/api') #register nlp blueprint
db = Database(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'nlp_app')
) # database instance
app.config['db'] = db
db.create_user_table() # create user table if not exists
db.create_analysis_history_table() # create analysis history table if not exists

@app.route('/')
def home():
    return render_template('login.html') #(course1="Data Science", course2="Machine Learning", course3="Deep Learning", course4="AI Basics", course5="NLP Fundamentals")

#login logic
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    user = db.validate_user(email, password)
    if user:
        session['user_id'] = user['id']
        session['user'] = user['first_name']
       # flash('Login successful!', 'success')
        return redirect(url_for('profile'))
    
    flash('Invalid email or password', 'error')
    return redirect(url_for('home'))
#register logic
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        if db.get_user_by_email(email):
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        db.add_user(first_name, last_name, email, password)
        flash('You are in! Please login.')
        return redirect(url_for('home'))
    return render_template('register.html')
@app.route('/profile')
def profile():
    if 'user' not in session or 'user_id' not in session:
        return redirect(url_for('home'))
    
    tab = request.args.get('tab','NER')  # Default to 'ner' tab
    analysis_history = db.get_user_analysis_history(session['user_id'])
    return render_template(
        'profile.html',
        active_tab=tab,
        analysis_history=analysis_history,
        app_name=APP_NAME,
        session=session
    )

# main module


#@app.route('/contactus')
#def contactus():
    #return jsonify({"contact no.": "1234567890", "email": "info@dsscience.com"})

if __name__ == '__main__': #running the scripts
    app.run(debug=True)
    



 
