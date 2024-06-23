from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from flask import session
import os
# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_PORT'] = 3307  # Note that the port is specified as an integer
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskdb'
mysql = MySQL(app)

# Now, initialize SQLAlchemy with the app

@app.route('/')
def index():
    return render_template('index.html') # Temporarily return a simple string

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        password = request.form['password']
      
        cur = mysql.connection.cursor()
        # i want to get the user id and name to display in the profile page

        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
           session['user_id'] = user[0]
           session['email'] = user[1]
           session['full_name'] = user[4]
           session['user_name'] = user[2]
        
           return redirect(url_for('index'))
    # If it's a GET request or the login failed, show the login form again
    return render_template('login.html')   
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        email = request.form['email']
        Name = request.form['name']
        password = request.form['password']
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO users (UserName, Email, Name, Password) VALUES (%s, %s, %s, %s)", (username, email, Name, password))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    # If it's a GET request or the registration failed, show the registration form again
    return render_template('signup.html')
@app.route('/yourteam')
def yourteam():
    cur=mysql.connection.cursor()
    cur.execute("SELECT Name, JerseyNumber, Position,PlayerID FROM players")
    all_players = cur.fetchall()  # Fetches all rows of a query result
    return render_template('yourteam.html', all_players=all_players)

@app.route('/myteam')
def yourteam_user():
    cur = mysql.connection.cursor()
    cur.execute("SELECT Name, JerseyNumber, Position, PlayerID FROM players WHERE PlayerID IN (SELECT PlayerID FROM userselections WHERE UserID = %s)", (session['user_id'],))
    user_team = cur.fetchall()
    if not user_team:
        flash('You have not selected any players yet!')
        cur.close()  # Ensure the cursor is closed even if an error occurs
        print(user_team)
        
    return render_template('myteam.html', user_team=user_team)


@app.route('/profile')
def profile():
    return render_template('profile.html')
@app.route('/submit_selected_players', methods=['POST'])
def submit_selected_players():
    if request.method == 'POST':
        selected_players = request.form.getlist('selected_players')
        cur = mysql.connection.cursor()
        for player in selected_players:
            cur.execute("INSERT INTO userselections (PlayerID, UserID) VALUES (%s, %s)", (player, session['user_id']))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('yourteam'))
    else:
        # Handle non-POST requests here. For example:
        return "Method Not Allowed", 405

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
@app.route('/upload-profile-photo', methods=['POST'])
def upload_profile_photo():
    if 'profile_photo' not in request.files:
        return redirect(request.url)
    file = request.files['profile_photo']
    if file.filename == '':
        return redirect(request.url)
    if file:  # If the file exists and is valid
        filename = secure_filename(file.filename)
        file.save(os.path.join('static/images/', filename))
        return redirect(url_for('profile'))  # Redirect to the profile page or wherever appropriate
if __name__ == '__main__':
    app.run(debug=True)