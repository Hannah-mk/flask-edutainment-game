from flask import Flask, render_template, request, redirect, flash, url_for, session, send_from_directory, abort
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
import os

app = Flask(__name__)
app.secret_key = "1234"  # Needed for flash messages

# --- MySQL Config ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db'

mysql = MySQL(app)

# --- Page Routes ---
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/levels')
def levels():
    return render_template('levels.html')

@app.route('/levels/gcse')
def gcse():
    return render_template('gcse.html')

@app.route('/levels/gcse/level1')
def gcse1():
    return render_template('gcse1.html')

@app.route('/levels/gcse/level2')
def level2():
    return render_template('gcse2.html')

@app.route('/levels/alevel')
def alevel():
    return render_template('alevel.html')

# --- Dynamic Game Routes ---
@app.route('/play/<level>/')
def play_level(level):
    # Path to the build/web folder for the requested level
    build_dir = os.path.join(app.static_folder, 'game', 'levels', level, 'build', 'web')
    index_path = os.path.join(build_dir, 'index.html')
    if not os.path.exists(index_path):
        abort(404)
    return send_from_directory(build_dir, 'index.html')

@app.route('/play/<level>/<path:filename>')
def play_asset(level, filename):
    # Serve JS, WASM, images, APKs, etc.
    build_dir = os.path.join(app.static_folder, 'game', 'levels', level, 'build', 'web')
    return send_from_directory(build_dir, filename)

# --- Authentication Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and 'password_hash' in user and check_password_hash(user['password_hash'], password):
            session['username'] = username
            session['profile_icon'] = user.get('profile_icon', 'default.svg')
            return redirect(url_for('home'))
        flash("Invalid username or password.", "error")

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for('signup'))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash("Username already taken. Please choose another.", "error")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, hashed_password)
        )
        mysql.connection.commit()
        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for('login'))

    username = session['username']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT profile_icon FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    icon = user['profile_icon'] if user else 'default.svg'

    return render_template('profile.html', username=username, user_profile_icon=icon)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    session.pop('profile_icon', None)
    return redirect(url_for('home'))

@app.route('/update_icon', methods=['POST'])
def update_icon():
    if 'username' not in session:
        flash("You must be logged in to do that.", "error")
        return redirect(url_for('login'))

    selected_icon = request.form.get('icon')
    if selected_icon:
        username = session['username']
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE users SET profile_icon = %s WHERE username = %s",
            (selected_icon, username)
        )
        mysql.connection.commit()
        session['profile_icon'] = selected_icon
    return redirect(url_for('profile'))

if __name__ == "__main__":
    app.run(debug=True)
