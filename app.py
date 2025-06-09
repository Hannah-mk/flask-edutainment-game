from flask import Flask, render_template, request, redirect, flash, url_for, session, send_from_directory, abort
from flask_mysql_connector import MySQL
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.secret_key = "1234"  # Needed for flash messages

# app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
# app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
# app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
# app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
# app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DATABASE'] = 'db'
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

@app.route('/levels/gcse/level<level>')
def show_gcse_level(level):
    try:
        return render_template(f'/GCSE/gcse{level}.html')
    except:
        abort(404)

# A-Level Level Routes
@app.route('/levels/alevel') # A-Level level selection page
def alevel():
    return render_template('alevel.html')

@app.route('/levels/alevel/level<level>')
def show_alevel_level(level):
    try:
        return render_template(f'/Alevel/alevel{level}.html')
    except:
        abort(404)

# Minigame Routes
@app.route('/levels/minigames') # A-Level level selection page
def minigames():
    return render_template('minigames.html')

@app.route('/levels/minigames/minigame<level>')
def show_minigame_level(level):
    try:
        return render_template(f'/Minigames/minigame{level}.html')
    except:
        abort(404)

@app.route('/levels/gcse/gcseminigame<level>')
def show_gcse_minigame_level(level):
    try:
        return render_template(f'/GCSE/GCSE_Minigames/gcse_minigame{level}.html')
    except:
        abort(404)

@app.route('/levels/alevel/alevelminigame<level>')
def show_alevel_minigame_level(level):
    try:
        return render_template(f'/Alevel/Alevel_Minigames/alevel_minigame{level}.html')
    except:
        abort(404)

# Cutscene Routes
@app.route('/levels/gcse/gcsecutscene<level>')
def show_gcse_cutscene(level):
    try:
        return render_template(f'/GCSE/GCSE_Cutscenes/gcse_cutscene{level}.html')
    except:
        abort(404)

@app.route('/levels/alevel/alevelcutscene<level>')
def show_alevel_cutscene(level):
    try:
        return render_template(f'/Alevel/Alevel_Cutscenes/alevel_cutscene{level}.html')
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
def play_minigame(level):
    # Path to the build/web folder for the requested level
    build_dir = os.path.join(app.static_folder, 'game', 'Minigame', level, 'build', 'web')
    index_path = os.path.join(build_dir, 'index.html')
    if not os.path.exists(index_path):
        abort(404)
    return send_from_directory(build_dir, 'index.html')

@app.route('/play minigame/<level>/<path:filename>')
def play_minigame_asset(level, filename):
    build_dir = os.path.join(app.static_folder, 'game', 'Minigame', level, 'build', 'web')
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
            session['profile_icon'] = user.get('profile_icon') or 'default.svg'
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

    # profile icon
    cursor.execute("SELECT profile_icon FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    icon = user['profile_icon'] if user else 'default.svg'

    # their friends
    cursor.execute("SELECT user2 AS friend_username FROM friends WHERE user1 = %s", (username,))
    friends = cursor.fetchall()  # list of dicts: [{ 'friend_username': 'alice' }, ...]

    return render_template(
      'profile.html',
      username=username,
      user_profile_icon=icon,
      friends_list=[f['friend_username'] for f in friends],
      search_results=None,
      search_performed=False
    )

@app.route('/add_friend', methods=['POST'])
def add_friend():
    if 'username' not in session:
        flash("Log in first to add friends.", "error")
        return redirect(url_for('login'))

    user1 = session['username']
    user2 = request.form['friend_username']

    if user1 == user2:
        flash("You can’t add yourself.", "error")
        return redirect(url_for('profile'))

    cursor = mysql.connection.cursor()
    try:
        cursor.execute(
          "INSERT INTO friends (user1, user2) VALUES (%s, %s)",
          (user1, user2)
        )
        mysql.connection.commit()
        flash(f"{user2} is now your friend!", "success")
    except Exception as e:
        # if it’s a duplicate key, they’re already friends
        flash(f"You’re already friends with {user2}.", "info")
    return redirect(url_for('profile'))

@app.route('/remove_friend', methods=['POST'])
def remove_friend():
    if 'username' not in session:
        return redirect(url_for('login'))

    user1 = session['username']
    user2 = request.form['friend_username']

    cursor = mysql.connection.cursor()
    cursor.execute(
      "DELETE FROM friends WHERE user1 = %s AND user2 = %s",
      (user1, user2)
    )
    mysql.connection.commit()
    flash(f"You’ve removed {user2}.", "success")
    return redirect(url_for('profile'))

@app.route('/search_user')
@login_required
def search_user():
    me    = session['username']
    query = request.args.get('search_username', '').strip()

    cursor = mysql.connection.cursor(dictionary=True)

    # 1) get your existing friends
    cursor.execute(
      "SELECT user2 AS friend_username FROM friends WHERE user1 = %s",
      (me,)
    )
    friend_rows = cursor.fetchall()
    friends_list = [r['friend_username'] for r in friend_rows]

    # 2) now do the search
    cursor.execute("""
      SELECT username
        FROM users
       WHERE username LIKE %s
         AND username != %s
         AND username NOT IN (
             SELECT user2 FROM friends WHERE user1 = %s
         )
    """, (f"%{query}%", me, me))
    results = cursor.fetchall()

    return render_template(
      "profile.html",
      username=me,
      user_profile_icon=session.get('profile_icon'),
      friends_list=friends_list,
      search_results=results,
      search_performed=True
    )

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