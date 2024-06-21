from flask import Flask,render_template,request,redirect,url_for
from flask_mysqldb import MySQL
# Initialize the Flask application
app = Flask(__name__)
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
        # Here, add your logic to validate the username and password
        # If the username and password are valid, you can redirect to another page
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
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

if __name__ == '__main__':
    app.run(debug=True)