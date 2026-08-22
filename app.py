# Portions of this code were developed with the assistance of Claude (Anthropic)
# and GitHub Copilot/VS Code autocompletion suggestions.

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, init_db
from werkzeug.utils import secure_filename
from processing import remove_duplicates


app = Flask(__name__)
app.secret_key = 'your_secret_key'

PROCESSING_FUNCTIONS = {
    'remove_duplicates': remove_duplicates,
}

import os

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

init_db()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(id=user['id'], email=user['email'], password_hash=user['password_hash'])
    return None

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required.')
            return redirect(url_for('register'))

        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if existing_user:
            flash('Email already registered.')
            conn.close()
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        conn.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, password_hash))
        conn.commit()
        conn.close()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required.')
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user is None or not check_password_hash(user['password_hash'], password):
            flash('Invalid email or password.')
            return redirect(url_for('login'))

        user_obj = User(id=user['id'], email=user['email'], password_hash=user['password_hash'])
        login_user(user_obj)

        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

import pandas as pd

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        processing_type = request.form.get('processing_type')

        if not file or file.filename == '':
            flash('Please select a file to upload.')
            return redirect(url_for('upload'))

        if not allowed_file(file.filename):
            flash('Invalid file type. Only CSV files are allowed.')
            return redirect(url_for('upload'))

        filename = secure_filename(file.filename)
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(upload_path)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (user_id, original_filename, processing_type, status) VALUES (?, ?, ?, ?)', 
                     (current_user.id, filename, processing_type, 'pending'))
        task_id = cursor.lastrowid        
        conn.commit()

        result_filename = f"result_{filename}"
        result_path = os.path.join(RESULT_FOLDER, result_filename)

        try:
            processing_function = PROCESSING_FUNCTIONS.get(processing_type)
            processing_function(upload_path, result_path)

            cursor.execute('UPDATE tasks SET status = ?, result_filename = ? WHERE id = ?',
                         ('done', result_filename, task_id))
            conn.commit()
            flash('File processed successfully.')
        except Exception as e:
            cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', ('error', task_id))
            conn.commit()
            flash(f'Error processing file: {str(e)}')
                
        conn.close()
        return redirect(url_for('upload_file'))

    return render_template('upload.html')

@app.route('/download/<int:task_id>')
@login_required
def download_file(task_id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, current_user.id)).fetchone()
    conn.close()

    if task is None:
        flash('Task not found.')
        return redirect(url_for('upload_file'))

    if task['status'] != 'done' or not task['result_filename']:
        flash('File is not ready for download.')
        return redirect(url_for('upload_file'))

    result_filename = task['result_filename']
    return send_from_directory(RESULT_FOLDER, result_filename, as_attachment=True)

@app.route('/history')
@login_required
def history():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC', (current_user.id,)).fetchall()
    conn.close()
    return render_template('history.html', tasks=tasks)

if __name__ == '__main__':
    app.run(debug=True)