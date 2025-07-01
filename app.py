from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import re
from werkzeug.utils import secure_filename
from resume_processor import process_resumes

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

UPLOAD_FOLDER = 'uploads/resumes'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Mock user database
USERS = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_email(email):
    if email is None:
        return False
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not is_valid_email(email):
            flash('Invalid email format.', 'error')
            return render_template('login.html')

        if email in USERS and USERS[email] == password:
            session['logged_in'] = True
            session['email'] = email
            # Initialize job description if not set
            if 'job_description' not in session:
                session['job_description'] = """We are looking for a Python developer with experience in:
- Machine Learning
- Natural Language Processing
- Flask/Django frameworks
- 3+ years of experience"""
            return redirect(url_for('dashboard'))
        else:
            flash('Wrong email or password.', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not is_valid_email(email):
            flash('Invalid email format.', 'error')
            return render_template('register.html')

        if email in USERS:
            flash('Email already registered.', 'error')
        else:
            USERS[email] = password
            flash('Registered successfully. Please login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    job_description = session.get('job_description', """We are looking for a Python developer with experience in:
- Machine Learning
- Natural Language Processing
- Flask/Django frameworks
- 3+ years of experience""")

    resumes_data = process_resumes(job_description)
    resumes_data.sort(key=lambda x: x.get("Overall Rank", 0), reverse=True)
    uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])

    return render_template('dashboard.html', resumes=resumes_data, files=uploaded_files, current_job_description=job_description)

@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    uploaded_files = request.files.getlist('file')
    job_description = request.form.get('job_description', '').strip()

    # Save job description in session for persistence
    session['job_description'] = job_description

    if not uploaded_files or all(f.filename == '' for f in uploaded_files):
        flash('No files selected.', 'error')
        return redirect(url_for('dashboard'))

    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash(f"Invalid file skipped: {file.filename}", 'error')

    flash('File(s) uploaded successfully.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_resume(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'{filename} has been deleted.', 'success')
    else:
        flash('File not found.', 'error')

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
