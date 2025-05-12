from flask import Flask, render_template, request, redirect, flash, url_for, session, send_from_directory, abort
from flask_mysql_connector import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.secret_key = "1234"  # Needed for flash messages

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))

mysql = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Page Routes ---
@app.route('/')  #Home page
def home():
    return render_template('home.html')

@app.route('/levels') #Levels selection page
def levels():
    return render_template('levels.html')

# GCSE Level Routes
@app.route('/levels/gcse') #GCSE level selection page
def gcse():
    return render_template('gcse.html')

@app.route('/levels/gcse/<level>')
def show_gcse_level(level):
    try:
        return render_template(f'GCSE/{level}.html')
    except:
        abort(404)

# A-Level Level Routes
@app.route('/levels/alevel') # A-Level level selection page
def alevel():
    return render_template('alevel.html')

@app.route('/levels/Alevel/<level>')
def show_alevel_level(level):
    try:
        return render_template(f'Alevel/{level}.html')
    except:
        abort(404)

# Minigame Routes
@app.route('/levels/<level>')
def show_minigame_level(level):
    try:
        return render_template(f'Minigame/{level}.html')
    except:
        abort(404)

# Cutscene Routes
@app.route('/levels/<level>')
def show_cutscene(level):
    try:
        return render_template(f'Cutscene/{level}.html')
    except:
        abort(404)

# --- Dynamic Game Routes ---
# GCSE
@app.route('/play gcse/<level>/')
def play_gcse_level(level):
    # Path to the build/web folder for the requested level
    build_dir = os.path.join(app.static_folder, 'game', 'GCSE', level, 'build', 'web')
    index_path = os.path.join(build_dir, 'index.html')
    if not os.path.exists(index_path):
        abort(404)
    return send_from_directory(build_dir, 'index.html')

@app.route('/play gcse/<level>/<path:filename>')
def play_gcse_asset(level, filename):
    build_dir = os.path.join(app.static_folder, 'game', 'GCSE', level, 'build', 'web')
    return send_from_directory(build_dir, filename)

#Alevel
@app.route('/play alevel/<level>/')
def play_alevel_level(level):
    # Path to the build/web folder for the requested level
    build_dir = os.path.join(app.static_folder, 'game', 'Alevel', level, 'build', 'web')
    index_path = os.path.join(build_dir, 'index.html')
    if not os.path.exists(index_path):
        abort(404)
    return send_from_directory(build_dir, 'index.html')

@app.route('/play alevel/<level>/<path:filename>')
def play_alevel_asset(level, filename):
    build_dir = os.path.join(app.static_folder, 'game', 'Alevel', level, 'build', 'web')
    return send_from_directory(build_dir, filename)

# Minigames
@app.route('/play minigame/<level>/')
def play_minigame_level(level):
    # Path to the build/web folder for the requested level
    build_dir = os.path.join(app.static_folder, 'game', 'Minigame', level, 'build', 'web')
    index_path = os.path.join(build_dir, 'index.html')
    if not os.path.exists(index_path):
        abort(404)
    return send_from_directory(build_dir, 'index.html')

@app.route('/play minigame/<level>/<path:filename>')
def play_minigame_asset(level, filename):
    build_dir = os.path.join(app.static_folder, 'game', 'Minigam', level, 'build', 'web')
    return send_from_directory(build_dir, filename)

#Cutscenes
@app.route('/play cutscene/<level>/')
def play_cutscene(level):
    # Path to the build/web folder for the requested level
    build_dir = os.path.join(app.static_folder, 'game', 'Cutscenes', level, 'build', 'web')
    index_path = os.path.join(build_dir, 'index.html')
    if not os.path.exists(index_path):
        abort(404)
    return send_from_directory(build_dir, 'index.html')

@app.route('/play cutscene/<level>/<path:filename>')
def play_cutscene_asset(level, filename):
    build_dir = os.path.join(app.static_folder, 'game', 'Cutscenes', level, 'build', 'web')
    return send_from_directory(build_dir, filename)

# --- Authentication Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_obj = User.get(username)
        login_user(user_obj)
        cursor = mysql.connection.cursor(dictionary=True)
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

        cursor = mysql.connection.cursor(dictionary=True)
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
    cursor = mysql.connection.cursor(dictionary=True)
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

@app.route('/search_user', methods=['POST'])
def search_user():
    if 'username' not in session:
        return redirect(url_for('login'))

    search_query = request.form['search_username']
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT username FROM users WHERE username LIKE %s", ('%' + search_query + '%',))
    users = cursor.fetchall()

    return render_template("profile.html", username=session['username'],
                           user_profile_icon=session.get('profile_icon'),
                           search_results=users,
                           search_performed=True)

@app.route('/add_friend', methods=['POST'])
@login_required
def add_friend():
    friend_username = request.form['friend_username']
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO friends (user1, user2) VALUES (%s, %s)", (current_user.username, friend_username))
    mysql.connection.commit()
    return redirect(url_for('profile'))


class User(UserMixin):
    def __init__(self, id, username, profile_icon):
        self.id = id
        self.username = username
        self.profile_icon = profile_icon

    @staticmethod
    def get(username):
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user:
            return None
        return User(id=user['id'], username=user['username'], profile_icon=user.get('profile_icon', 'default.svg'))

    @staticmethod
    def get_by_id(user_id):
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return None
        return User(id=user['id'], username=user['username'], profile_icon=user.get('profile_icon', 'default.svg'))

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


# Only needed for local dev, not when using gunicorn
if __name__ == "__main__":
    app.run()