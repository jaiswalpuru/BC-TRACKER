from flask import Flask, render_template, request, redirect, url_for, session
from markupsafe import escape
from flaskext.mysql import MySQL
import pymysql
import re, yaml, io

app = Flask(__name__)

with open("config.yaml", "r") as stream:
    data_loaded = yaml.safe_load(stream)

config = data_loaded['DATABASE']

app.secret_key = 'password123'
app.config['MYSQL_DATABASE_USER'] = config['USERNAME']
app.config['MYSQL_DATABASE_PASSWORD'] = config['PASSWORD']
app.config['MYSQL_DATABASE_DB'] = config['DB']

mysql = MySQL(app)

@app.route("/")
@app.route("/login", methods=['GET','POST'])
def login():
    display_message = ''
    if request.method=='POST' and 'username' in request.form and 'password' in request.form:
        user_name = request.form['username']
        password = request.form['password']
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT * FROM Users WHERE UserName = %s AND Password = %s',(user_name, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            msg = 'Logged in successfully !'
            return render_template('index.html', msg=display_message)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=display_message)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and \
            'email' in request.form and phone in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT * FROM Users WHERE UserName = % s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO Users VALUES (NULL, % s, % s, % s, %s, %s)', (username, password, email, phone, "User",))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)