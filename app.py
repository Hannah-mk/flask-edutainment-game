from flask import Flask, render_template, request, redirect, flash, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = "1234"  # Needed for flash messages

# --- MySQL Config ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/levels')
def levels():
    return render_template('levels.html')

@app.route('/levels/gcse')
def gcse():
    return render_template('gcse.html')

@app.route('/levels/alevel')
def alevel():
    return render_template('alevel.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(password)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        # Debugging: Check the retrieved user data
        print("Retrieved user:", user)

        if user:
            # Check if the password exists in the user data
            if 'password_hash' not in user:
                flash("Password field missing in user data.", "error")
                return redirect(url_for('login'))
            print((user['password_hash'], password))
            # Check the password hash
            if check_password_hash(user['password_hash'], password):
                flash("Login successful!", "success")
                return redirect(url_for('home'))  # Redirect to home page on successful login
            else:
                flash("Invalid username or password.", "error")
                return redirect(url_for('login'))  # Always redirect to the login page
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))

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
        user = cursor.fetchone()

        if user:
            flash("Username already taken. Please choose another.", "error")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)

        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

# Serve the main game file
@app.route('/game_file')
def game_file():
    return send_from_directory('static/pygame/build/web', 'index.html')

# Serve other game assets (JS, WASM, DATA files)
@app.route('/pygame/build/web/<path:filename>')
def serve_game_files(filename):
    return send_from_directory('static/pygame/build/web', filename)

if __name__ == "__main__":
    app.run(debug=True)
