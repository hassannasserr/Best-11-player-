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


@app.route('/')
def index():
    return render_template('index.html') # Temporarily return a simple string

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            return render_template('login.html', error="You need to enter both a username and a password.")
        cur = mysql.connection.cursor()
        # i want to get the user id and name to display in the profile page

        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        if not cur.rowcount:
            return render_template('login.html', error="The username or password is incorrect.")
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
        if not username or not email or not Name or not password:
            return render_template('signup.html', error="You need to enter all the required fields.")
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if user:
            return render_template('signup.html', error="The username is already taken.")
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user1 = cur.fetchone()
        if user1:
            return render_template('signup.html', error="The email is already taken.")
        else:
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
    if 'user_id' not in session:
        return render_template('myteam.html', error="You need to login to view your team.")
    else:
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT Name, JerseyNumber, Position, PlayerID FROM players WHERE PlayerID IN (SELECT PlayerID FROM userselections WHERE UserID = %s)", (session['user_id'],))
            user_team = cur.fetchall()
        finally:
            cur.close()
        return render_template('myteam.html', user_team=user_team)
    
    # Safety net: return a generic response if none of the above conditions are met

   
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('full_name', None)
    session.pop('user_name', None)
    return redirect(url_for('index'))        
    

@app.route('/delete', methods=['POST'])
def delete():
    player_ids = request.form.getlist('selected_players[]')  # Adjusted to handle multiple selections
    if not player_ids:
        flash("You need to select at least one player to delete.", "error")  # Use flash for error messages
        return redirect(url_for('yourteam_user'))
    else:
        cur = mysql.connection.cursor()
        try:
            # Use executemany or loop through player_ids to delete multiple
            query = "DELETE FROM userselections WHERE PlayerID = %s AND UserID = %s"
            # Prepare a list of tuples for each player_id to delete
            values = [(player_id, session['user_id']) for player_id in player_ids]
            cur.executemany(query, values)
            mysql.connection.commit()
        except Exception as e:
            flash(f"An error occurred: {e}", "error")  # Flash any exception as an error message
        finally:
            cur.close()
        flash("Selected players were successfully deleted.", "success")  # Success message
        return redirect(url_for('yourteam_user'))


@app.route('/profile')
def profile():
    return render_template('profile.html')
@app.route('/submit_selected_players', methods=['POST'])
def submit_selected_players():
    if request.method == 'POST':
        if 'user_id' not in session:
            return render_template('yourteam.html', error="You need to login to select players.")
        selected_players = request.form.getlist('selected_players')
        cur = mysql.connection.cursor()
        for player in selected_players:
            cur.execute("INSERT INTO userselections (PlayerID, UserID) VALUES (%s, %s)", (player, session['user_id']))
        mysql.connection.commit()
        cur.close()
        flash("Players have been added successfully", "success")  # 'success' is a category, you can customize it
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

@app.route('/contact', methods=['POST'])
def send_email():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        message = request.form['message']
        if not email or not name or not message:
            return render_template('index.html', error="You need to enter all the required fields.")
        cur=mysql.connection.cursor()
        cur.execute("insert into messages (Email, Name, Message) values (%s, %s, %s)", (email, name, message))
        mysql.connection.commit()
        cur.close()
        flash("Your message has been sent successfully.", "success")  # 'success' is a category, you can customize it
# Then redirect without the error argument
        return redirect(url_for('index'))  # Assuming 'index' is the view function for the homepage

@app.route('/change-password', methods=['POST'])
def change_password():
    if request.method == 'POST':
        if 'user_id' not in session:
            return render_template('profile.html', error="You need to login to change your password.")
        old_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if not old_password or not new_password or not confirm_password:
            return render_template('profile.html', error="You need to enter all the required fields.")
        if new_password != confirm_password:
            return render_template('profile.html', error="The new password and confirm password do not match.")
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE ID = %s AND Password = %s", (session['user_id'], old_password))
        user = cur.fetchone()
        if not user:
            return render_template('profile.html', error="The old password is incorrect.")
        cur.execute("UPDATE users SET Password = %s WHERE ID = %s", (new_password, session['user_id']))
        mysql.connection.commit()
        cur.close()
        flash("Your password has been changed successfully.", "success")
        return redirect(url_for('profile'))

    return render_template('profile.html')
if __name__ == '__main__':
    app.run(debug=True)