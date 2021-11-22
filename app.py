from flask import Flask, render_template, request, redirect, url_for, session
from markupsafe import escape
from flaskext.mysql import MySQL
import pymysql
import re, yaml, io
import datetime

app = Flask(__name__)

# load the config values from yaml file
with open("config.yaml", "r") as stream:
    data_loaded = yaml.safe_load(stream)

config = data_loaded['DATABASE']

# initialize all the key value pairs required for the mysql connection
app.secret_key = 'password123'
app.config['MYSQL_DATABASE_USER'] = config['USERNAME']
app.config['MYSQL_DATABASE_PASSWORD'] = config['PASSWORD']
app.config['MYSQL_DATABASE_DB'] = config['DB']

mysql = MySQL(app)

# Will store the response of sql query in a 2d matrix and return
def beautify_data_sql_response(data):
    res = []

    for row in range(len(data)):
        temp = []
        for col in range(len(data[row])):
            if isinstance(data[row][col], datetime.datetime):
                t = data[row][col]
                t = t.isoformat()
                temp.append(t)
            else:
                temp.append(data[row][col])
        res.append(temp)

    return res

#--------------------Needs to completed--------------------------------------------
#Fetch the data which need to be shown to respective user.
def get_data(user_type):
    cursor = mysql.get_db().cursor()

    if user_type == 'user':
        return 'user'
    elif user_type == 'admin':
        return 'admin'
    else :
        cursor.execute('SELECT * FROM Transaction WHERE Status = %s ', ("pending", ))
        data  = cursor.fetchall()
        return beautify_data_sql_response(data)

# homepage/login route
@app.route("/")
@app.route("/login", methods=['GET','POST'])
def login():
    msg = ''
    user_type = ''
    file_load=''

    if request.method=='POST' and 'username' in request.form and 'password' in request.form and \
            ('checkuser' in request.form or 'checkadmin' in request.form or 'checktrader' in request.form):
        user_name = request.form['username']
        password = request.form['password']
        if 'checkuser' in request.form :
            user_type = 'user'
            file_load = 'index.html'
        elif 'checktrader' in request.form:
            user_type = 'trader'
            file_load = 'trader.html'
        else:
            user_type = 'admin'
            file_load = 'admin.html'

        # get data based on the user type and render that specific template
        data = get_data(user_type)
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT * FROM Users WHERE UserName = %s AND Password = %s and Type = %s ',(user_name, password, user_type,))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            msg = 'Logged in successfully !'
            return render_template(file_load, msg=msg, data=data)
        else:
            msg = 'Incorrect username / password !'

    return render_template('login.html', msg=msg)

# logout route
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)

    return redirect(url_for('login'))

# sign up route
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and \
            'email' in request.form and 'phone' in request.form and 'phone' in request.form and 'staddress' in request.form and \
            'city' in request.form and 'zip' in request.form and 'state' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        zip = request.form['zip']
        state = request.form['state']
        city = request.form['city']
        street_address = request.form['staddress']
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT * FROM USERS WHERE UserName = %s ', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email or not phone:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO USERS VALUES (NULL, % s, % s, % s, %s, %s)', (username, password, phone, email, "user",))
            cursor.execute('SELECT ClientId FROM USERS WHERE UserName = %s ', (username,))
            client_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO ADDRESS VALUES (%s, %s, %s, %s, %s)', (client_id, street_address, city, state, zip))
            cursor.execute('INSERT INTO ACC_DETAILS VALUES (%s, %s, %s)', (client_id, '100000', '100000'))
            mysql.get_db().commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'

    return render_template('register.html', msg=msg)

# fetch all the data for a specific user from Transaction table based on the client_id
@app.route('/userdata/<client_id>')
def userdata(client_id):
    msg=''

    # fetch the users past transactions
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM Transaction WHERE ClientId = %s AND DATE < NOW() AND Status != %s ', (client_id,"pending", ))
    data = cursor.fetchall()

    # if the length of data fetched from sql is zero, this means that the user is trading for the first time
    if len(data)==0:
        msg='This is the first transaction'

    return render_template('userdata.html', msg=msg, data=data)