from flask import Flask, render_template, request, redirect, url_for, session
from flask_caching import Cache
from markupsafe import escape
from flaskext.mysql import MySQL
import pymysql
import re, yaml, io
import datetime
import json
import base64
from adapters.api_calls_one import *
from helpers.helpers import *
from cryptography.fernet import Fernet

app = Flask(__name__)

# cache config
cache_config = {
    "DEBUG" : True,
    "CACHE_TYPE" : "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT" : 100000
}
app.config.from_mapping(cache_config)
cache = Cache(app)

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

config_app = data_loaded['APP']
key = config_app["KEY"]
cipher = Fernet(key)

# to update the user account balance
def update_acc_balance(client_id, balance):
    updated = False
    cursor = mysql.get_db().cursor()
    try:
        cursor.execute('UPDATE ACC_DETAILS SET FiatCurrency = %s WHERE ClientId= %s ', (balance, client_id, ))
        mysql.get_db().commit()
        updated = True
    finally:
        return updated

# update bitcoin amount
def update_user_bitcoin_amt(client_id, bitcoin):
    updated = False
    cursor = mysql.get_db().cursor()
    try:
        cursor.execute('UPDATE BITCOIN SET Units = %s WHERE ClientId = %s', (bitcoin, client_id, ))
        mysql.get_db().commit()
        updated = True
    finally:
        return updated

# implementation needs to be done properly, only one function to query the result, which will be called by all the API's
def execute(query):
    cursor = mysql.get_db().cursor()

    cursor.execute(query)
    data = cursor.fetchall()
    return beautify_sql_response_pending_transaction(data)

# will store the response of sql query in a 2d matrix and return
def beautify_sql_response_pending_transaction(data):
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

# update transaction table based on the decision of the user
def update_transaction_table(client_decision):
    print(client_decision)
    cursor = mysql.get_db().cursor()

    for val in client_decision:
        if val['transaction_type'] == 'BUY':

            commission_rate = 0
            client_id = int(val['client_id'])
            recipient_id = int(val['recipient_id'])
            commission_rate_type = val['commission_rate_type']
            commission_paid = float(val['commission_paid'])
            decision = val['decision']
            bitcoin_amt = float(val['bitcoin_amt'])
            rate = float(val['commission_type'])

            # get the buyer account details
            cursor.execute('SELECT * FROM ACC_DETAILS WHERE ClientId = %s', (client_id, ))
            buyer_acc_detail = cursor.fetchone()

            # get the seller account detail
            cursor.execute('SELECT * FROM ACC_DETAILS WHERE ClientId = %s', (recipient_id,))
            seller_acc_detail = cursor.fetchone()

            #get the user bitcoin account details
            cursor.execute('SELECT * FROM BITCOIN WHERE ClientId = %s', (client_id, ))
            buyer_bitcoin_detail = cursor.fetchone()

            # get the seller bitcoin detail
            cursor.execute('SELECT * FROM BITCOIN WHERE ClientId = %s', (recipient_id,))
            seller_bitcoin_detail = cursor.fetchone()

            # get the commission paid by the seller
            cursor.execute('SELECT * FROM Seller WHERE ClientId = %s', (recipient_id, ))
            seller_log = cursor.fetchone()

            seller_commission_rate_type = seller_log[5]
            seller_commission_paid = float(seller_log[3])
            seller_bitcoin_sell_amt = float(seller_log[1])

            # commission rate for buyer at the time of buying
            buyer_bitcoin_commission_rate = (commission_paid * 100)/(rate * bitcoin_amt)

            # commission rate for seller at the time of selling
            seller_bitcoin_commission_rate = (seller_commission_paid * 100)/(int(seller_log[4])*bitcoin_amt)

            commission_rate_in_bitcoin = commission_paid / buyer_bitcoin_commission_rate
            seller_rate_in_bitcoin = seller_commission_paid / seller_bitcoin_commission_rate
            commission_rate_in_fiat_buyer = 0
            commission_rate_in_fiat_seller = 0

            if decision == 'completed':
                if commission_rate_type == 'fiat' and seller_commission_rate_type == 'fiat':
                    #client = fiat and seller = fiat

                    # buyer
                    cursor.execute('UPDATE ACC_DETAILS SET FiatCurrency = %s WHERE ClientId = %s',
                                   (buyer_acc_detail[1]-commission_paid - (bitcoin_amt * get_current_rate()), client_id))

                    # seller
                    cursor.execute('UPDATE ACC_DETAILS SET FiatCurrency = %s WHERE ClientId = %s',
                                   (seller_acc_detail[1]-seller_commission_paid+(bitcoin_amt*get_current_rate()), recipient_id))

                    if float(seller_bitcoin_detail[1]) - bitcoin_amt == 0:
                        cursor.execute('DELETE FROM Seller WHERE ClientId = %s',(recipient_id, ))
                    else :
                        # calculate the bitcoin amount and update the seller table
                        cursor.execute('UPDATE Seller SET Units = %s, CommisionPaid = %s WHERE ClientId = %s',
                                       (seller_bitcoin_sell_amt-bitcoin_amt,
                                        seller_commission_paid - ((seller_bitcoin_sell_amt - bitcoin_amt) *
                                                                  seller_bitcoin_commission_rate * int(seller_log[4])/100),
                                        recipient_id, ))

                    cursor.execute('UPDATE BITCOIN SET Units = %s WHERE ClientId = %s',
                                   (float(buyer_bitcoin_detail[1])+bitcoin_amt, client_id))
                    cursor.execute('UPDATE BITCOIN SET Units = %s WHERE ClientId = %s',
                                   (float(seller_bitcoin_detail[1])-bitcoin_amt, recipient_id))

                elif commission_rate == 'fiat' and seller_commission_rate_type == 'bitcoin':

                    # buyer
                    cursor.execute('UPDATE ACC_DETAILS SET FiatCurrency = %s WHERE ClientId = %s',
                                   (buyer_acc_detail[1]-commission_paid - (bitcoin_amt * get_current_rate()), client_id))

                    # seller
                    cursor.execute('UPDATE BITCOIN SET Units = %s WHERE ClientId = %s',
                                   (float(seller_bitcoin_detail[1]) - bitcoin_amt, recipient_id,))

                    if seller_rate_in_bitcoin < (float(seller_bitcoin_detail[1]) - bitcoin_amt):
                        cursor.execute('UPDATE BITCOIN SET Units = %s WHERE ClientId = %s',
                                       (float(seller_bitcoin_detail[1]) - bitcoin_amt - seller_rate_in_bitcoin),
                                       recipient_id, )
                    else:
                        left_bitcoin_seller = seller_rate_in_bitcoin - float(seller_bitcoin_detail[1])
                        commission_rate_in_fiat_seller = left_bitcoin_seller * seller_bitcoin_commission_rate
                        cursor.execute('UPDATE BITCOIN SET Units = %s AND ClientId = %s',
                                       (0, recipient_id,))
                        cursor.execute('UPDATE ACC_DETAILS SET FiatCurrency = %s AND ClientId = %s',
                                       (float(seller_acc_detail[1]) - commission_rate_in_fiat_seller, recipient_id,))

                    if float(seller_bitcoin_detail[1]) - bitcoin_amt == 0:
                        cursor.execute('DELETE FROM Seller WHERE ClientId = %s', (recipient_id,))
                    else:
                        # calculate the bitcoin amount and update the seller table
                        cursor.execute('UPDATE Seller SET Units = %s, CommisionPaid = %s WHERE ClientId = %s',
                                       (seller_bitcoin_sell_amt - bitcoin_amt,
                                        seller_commission_paid - ((seller_bitcoin_sell_amt - bitcoin_amt) *
                                                                  seller_bitcoin_commission_rate * int(
                                                    seller_log[4]) / 100),
                                        recipient_id,))

                elif commission_rate == 'bitcoin' and seller_commission_rate_type == 'fiat':

                    # buyer
                    if commission_rate_in_bitcoin < float(buyer_bitcoin_detail[1]):
                        cursor.execute('UPDATE BITCOIN SET Units = %s WHERE ClientId = %s',
                                       (float(buyer_bitcoin_detail[1]) - commission_rate_in_bitcoin + bitcoin_amt,
                                        client_id,))
                    else:
                        left_bitcoin_buyer = commission_rate_in_bitcoin - float(buyer_bitcoin_detail[1])
                        commission_rate_in_fiat_buyer = left_bitcoin_buyer * buyer_bitcoin_commission_rate
                        cursor.execute('UPDATE BITCOIN SET Units = %s WHERE ClientId = %s',
                                       (bitcoin_amt, client_id,))
                        cursor.execute('UPDATE ACC_DETAILS SET FiatCurrency = %s WHERE ClientId = %s',
                                       (buyer_acc_detail[1] - commission_rate_in_fiat_buyer, client_id,))

                    # seller
                    cursor.execute('UPDATE ACC_DETAILS SET FiatCurrency = %s WHERE ClientId = %s',
                                   (seller_acc_detail[1] - seller_commission_paid + (bitcoin_amt * get_current_rate()),
                                    recipient_id))

                    if float(seller_bitcoin_detail[1]) - bitcoin_amt == 0:
                        cursor.execute('DELETE FROM Seller WHERE ClientId = %s', (recipient_id,))
                    else:
                        # calculate the bitcoin amount and update the seller table
                        cursor.execute('UPDATE Seller SET Units = %s, CommisionPaid = %s WHERE ClientId = %s',
                                       (seller_bitcoin_sell_amt - bitcoin_amt,
                                        seller_commission_paid - ((seller_bitcoin_sell_amt - bitcoin_amt) *
                                                                  seller_bitcoin_commission_rate * int(
                                                    seller_log[4]) / 100),
                                        recipient_id,))

                    cursor.execute('UPDATE BITCOIN SET Units = %s WHERE ClientId = %s',
                                   (float(buyer_bitcoin_detail[1]) + bitcoin_amt, client_id))
                    cursor.execute('UPDATE BITCOIN SET Units = %s WHERE ClientId = %s',
                                   (float(seller_bitcoin_detail[1]) - bitcoin_amt, recipient_id))

                else:
                    # client = bitcoin and seller = bitcoin

                    # buyer
                    if commission_rate_in_bitcoin < float(buyer_bitcoin_detail[1]) :
                        cursor.execute('UPDATE BITCOIN SET Units = %s WHERE ClientId = %s',
                                       (float(buyer_bitcoin_detail[1])-commission_rate_in_bitcoin+bitcoin_amt, client_id, ))
                    else :
                        left_bitcoin_buyer = commission_rate_in_bitcoin-float(buyer_bitcoin_detail[1])
                        commission_rate_in_fiat_buyer = left_bitcoin_buyer * buyer_bitcoin_commission_rate
                        cursor.execute('UPDATE BITCOIN SET Units = %s WHERE ClientId = %s',
                                       (bitcoin_amt, client_id, ))
                        cursor.execute('UPDATE ACC_DETAILS SET FiatCurrency = %s WHERE ClientId = %s',
                                       (buyer_acc_detail[1]-commission_rate_in_fiat_buyer, client_id, ))


                    #seller
                    cursor.execute('UPDATE BITCOIN SET Units = %s WHERE ClientId = %s',
                                    (float(seller_bitcoin_detail[1]) - bitcoin_amt, recipient_id,))

                    if seller_rate_in_bitcoin < (float(seller_bitcoin_detail[1])-bitcoin_amt) :
                        cursor.execute('UPDATE BITCOIN SET Units = %s WHERE ClientId = %s',
                                       (float(seller_bitcoin_detail[1])-bitcoin_amt-seller_rate_in_bitcoin), recipient_id, )
                    else :
                        left_bitcoin_seller = seller_rate_in_bitcoin-float(seller_bitcoin_detail[1])
                        commission_rate_in_fiat_seller = left_bitcoin_seller * seller_bitcoin_commission_rate
                        cursor.execute('UPDATE BITCOIN SET Units = %s AND ClientId = %s',
                                       (0, recipient_id, ))
                        cursor.execute('UPDATE ACC_DETAILS SET FiatCurrency = %s AND ClientId = %s',
                                       (float(seller_acc_detail[1])-commission_rate_in_fiat_seller, recipient_id, ))

                    if float(seller_bitcoin_detail[1]) - bitcoin_amt == 0:
                        cursor.execute('DELETE FROM Seller WHERE ClientId = %s',(recipient_id, ))
                    else :
                        # calculate the bitcoin amount and update the seller table
                        cursor.execute('UPDATE Seller SET Units = %s, CommisionPaid = %s WHERE ClientId = %s',
                                       (seller_bitcoin_sell_amt - bitcoin_amt,
                                        seller_commission_paid - ((seller_bitcoin_sell_amt - bitcoin_amt) *
                                                                  seller_bitcoin_commission_rate * int(seller_log[4]) / 100),
                                        recipient_id,))

            cursor.execute('UPDATE Transaction SET Status = %s WHERE ClientId = %s',(decision, client_id, ) )

            mysql.get_db().commit()
    return True

# fetch the data which need to be shown to respective user.
def get_pending_data(user_type, client_id=0):

    if user_type == 'silver' or user_type == 'gold':
        return execute('SELECT * FROM TRANSACTION WHERE ClientId = {} AND Status = "{}"'.format(client_id, "pending"))
    elif user_type == 'admin':
        return execute('SELECT * FROM TRANSACTION')
        data = cursor.fetchall()
    else :
        return execute('SELECT * FROM TRANSACTION WHERE Status = "{}"'.format("pending"))


# get pending transaction which is not is not of the current user
def get_pending_data_except_current_user(client_id):

    data = execute('SELECT u.UserName, s.Units, s.ClientId  FROM Seller s JOIN Users u ON s.ClientId=u.ClientId'
                   ' WHERE s.ClientId != {} '.format(client_id))
    return data

# get details of bitcoin
def get_user_bitcoin_details(client_id):
    units = execute('SELECT Units FROM BITCOIN WHERE ClientId = {}'.format(client_id))

    if len(units)==0:
        return 0
    return units[0][0]

# get balance details
def get_account_details(client_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM ACC_DETAILS WHERE ClientId = %s', (client_id, ))
    res = cursor.fetchone()
    if res is None:
        return None
    return list(res)

# get the users details or the status based on the flag return_status
def get_user_details(user_name, password, user_type, return_status):
    cursor = mysql.get_db().cursor()

    if not return_status:
        cursor.execute('SELECT * FROM Users WHERE UserName = %s AND Type IN %s ',
                       (user_name, user_type,))
        account = cursor.fetchone()
        password_decrypt = cipher.decrypt(bytes(account[4],'utf-8')).decode('utf-8')
        if password_decrypt != password:
            return None
        if account is None:
            return None
        return list(account)
    else:
        cursor.execute('SELECT Type FROM Users WHERE UserName = %s', (user_name, ))
        status = cursor.fetchone()
        return status[0]

# make session time 5 min
@app.before_request
def make_session_permanent():
    session.permanent = True;
    app.permanent_session_lifetime = datetime.timedelta(minutes=5)

# credit into users account
@app.route("/credit_balance", methods=['POST'])
def credit_balance():
    data = get_json_data(request.data)
    client_id = session['id']
    credit_amt = float(data['credit_amt'])
    fiat_balance = float(data['cur_balance'])
    if update_acc_balance(client_id, fiat_balance+credit_amt):
        return json.dumps({'success':'True'})
    else:
        return json.dumps({'success':'False'})

# debit from users account
@app.route("/debit_balance", methods=['POST'])
def debit_balance():
    data = get_json_data(request.data)
    client_id = session['id']
    fiat_balance = float(data['cur_balance'])
    debit_amt = float(data['credit_amt'])

    if fiat_balance < debit_amt:
        return json.dumps({'success': False})

    if update_acc_balance(client_id, fiat_balance-debit_amt):
        return json.dumps({'success':'True'})
    else:
        return json.dumps({'success': False})

# credit bitcoin into users account
@app.route("/credit_bitcoin", methods=['POST'])
def credit_bitcoin():
    data = get_json_data(request.data)
    client_id = session['id']
    bitcoin_amt = float(data['curr_bitcoin'])
    bitcoin_credit = float(data['bitcoin'])

    if update_user_bitcoin_amt(client_id, bitcoin_amt+bitcoin_credit):
        return json.dumps({'success':'True'})
    else:
        return json.dumps({'success' : False})

# debit bitcoin from users account
@app.route("/debit_bitcoin", methods=['POST'])
def debit_bitcoin():
    data = get_json_data(request.data)
    client_id = session['id']
    bitcoin_amt = float(data['curr_bitcoin'])
    bitcoin_debit = float(data['bitcoin'])

    if bitcoin_debit > bitcoin_amt:
        return json.dumps({'success':False})

    if update_user_bitcoin_amt(client_id,bitcoin_amt-bitcoin_debit):
        return json.dumps({'success':'True'})
    else:
        return json.dumps({'success':False})

# homepage/login route
@app.route("/")
@app.route("/login", methods=['GET','POST'])
def login():
    msg = ''
    user_type = ''
    file_load=''
    data = ''
    acc_details = []
    account = []
    pending_transaction = ''

    # check is user is already logged in
    if len(session) > 1 :
        acc_details = get_account_details(session['id'])
        membership_type = get_user_details(session['username'], '', '', True)
        data = get_pending_data(membership_type,session['id'])
        pending_transaction = get_pending_data_except_current_user(session['id'])
        units = get_user_bitcoin_details(session['id'])
        return render_template(session['file_redirect'], msg=session['msg'], data=data, acc_details=acc_details,
                               membership_type=membership_type, bitcoin_unit=units, bitcoin_rate=get_current_rate(),
                               pending_transaction=pending_transaction)

    if request.method=='POST' and 'username' in request.form and 'password' in request.form and \
            ('checkuser' in request.form or 'checkadmin' in request.form or 'checktrader' in request.form):
        user_name = request.form['username']
        password = request.form['password']
        if 'checkuser' in request.form :
            user_type = ['silver','gold']
            file_load = 'index.html'
        elif 'checktrader' in request.form:
            user_type = ['trader']
            file_load = 'trader.html'
        else:
            user_type = ['admin']
            file_load = 'admin.html'

        #check if the user exists in db or no
        account = get_user_details(user_name, password, user_type, False)

        if account:
            # get the account details associated with the user
            acc_details = get_account_details(account[0])
            msg = 'Logged in successfully !'

            # get user bitcoin units of a user
            units = get_user_bitcoin_details(account[0])

            # get data based on the user type and render that specific template
            data = get_pending_data(account[7], account[0])

            # get pending transaction which are not of the current user
            pending_transaction = get_pending_data_except_current_user(account[0])

            #store in session
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            session['file_redirect'] = file_load
            session['msg'] = msg
            return render_template(file_load, msg=msg, data=data, acc_details=acc_details,
                                   membership_type=account[7], bitcoin_unit=units, bitcoin_rate=get_current_rate(),
                                   pending_transaction=pending_transaction)
        else:
            msg = 'Incorrect username / password !'

    return render_template('login.html', msg=msg)

# logout route
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('file_redirect', None)
    session.pop('msg', None)
    return redirect(url_for('login'))

# sign up route
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'firstname' in request.form and 'lastname' in request.form and \
            'password' in request.form and 'email' in request.form and 'phone' in request.form and 'phone' in request.form and \
            'staddress' in request.form and 'city' in request.form and 'zip' in request.form and 'state' in request.form:
        username = request.form['username']
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        password = cipher.encrypt(str.encode(request.form['password']))
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
            cursor.execute('INSERT INTO USERS VALUES (NULL, % s, %s, %s, % s, % s, %s, %s)', (username, first_name, last_name,
                                                                                      password, phone, email, "silver",))
            cursor.execute('SELECT ClientId FROM USERS WHERE UserName = %s ', (username,))
            client_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO ADDRESS VALUES (%s, %s, %s, %s, %s)', (client_id, street_address, city, state, zip))

            # inserting dummy data in acc and bitcoin table
            bitcoin_rate = get_current_rate()
            cursor.execute('INSERT INTO ACC_DETAILS VALUES (%s, %s)', (client_id, '100000'))
            cursor.execute('INSERT INTO BITCOIN VALUES (%s, %s)',( client_id, 2))
            mysql.get_db().commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'

    return render_template('register.html', msg=msg)

# fetch all the data for a specific user from Transaction table based on the client_id
@app.route('/userdata/<client_id>')
def userdata(client_id):
    msg=''

    #check if session is lost
    if len(session) == 0 :
        return render_template('login.html')

    # fetch the users past transactions
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM Transaction WHERE ClientId = %s AND DATE < NOW() AND Status != %s ', (client_id,"pending", ))
    data = cursor.fetchall()

    # if the length of data fetched from sql is zero, this means that the user is trading for the first time
    if len(data) == 0:
        msg='This is the first transaction'

    return render_template('userdata.html', msg=msg, data=data)

# this will insert the details in seller table regarding the details of the seller
@app.route('/sell_bitcoin', methods=['POST'])
def sell_bitcoin():
    obj = get_json_data(request.data)
    client_id = obj["ClientId"]
    # transaction_id = obj["TransactionId"]
    # transaction_type = obj["TransactionType"]
    membership_type = obj["MembershipType"]
    bitcoin_unit_to_sold = obj["BitcoinSell"]

    commission_rate_type = obj["CommissionType"]
    commission_type = get_tax_rate(membership_type)

    rate = get_current_rate()
    commission_paid = float(bitcoin_unit_to_sold) * float(rate)/100

    cursor = mysql.get_db().cursor()

    # first check if the user is already exists in the selling table, if yes then he won't be allowed to do thee transaction
    cursor.execute('SELECT * FROM SELLER WHERE ClientId = %s', (client_id, ))
    past_history = cursor.fetchall()

    if past_history:
        return json.dumps({'success': False})

    cursor.execute('INSERT INTO SELLER VALUES (%s, %s, %s, %s, %s, %s)',
                   (client_id, bitcoin_unit_to_sold, get_current_datetime(), commission_paid, commission_type, commission_rate_type))
    mysql.get_db().commit()
    return json.dumps({'success':True})

# create an entry in the transaction table for the current transaction
@app.route('/buy_bitcoin', methods=['POST'])
def buy_bitcoin():
    obj = get_json_data(request.data)
    client_id = obj["ClientId"]
    recipient_id = obj["RecipientId"]
    transaction_id = obj["TransactionId"]
    membership_type = obj["MembershipType"]
    bitcoin_unit_to_buy = obj["BitcoinBuy"]

    commission_rate_type = obj["CommissionType"]
    commission_type = get_tax_rate(membership_type)

    rate = get_current_rate()
    commission_paid = float(bitcoin_unit_to_buy) * float(rate)/100

    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM TRANSACTION WHERE ClientId = %s AND RecipientId = %s AND Status = %s ', (client_id, recipient_id,"pending", ))
    past_history = cursor.fetchall()

    if past_history:
        return json.dumps({'success':False})

    cursor.execute('INSERT INTO TRANSACTION VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                   (client_id, transaction_id, "BUY", get_current_datetime(), commission_paid,
                    commission_type, recipient_id, bitcoin_unit_to_buy, 'pending', commission_rate_type,))
    mysql.get_db().commit()

    return json.dumps({'success':True})

# update a list of transactions which is selected by the trader
@app.route('/update_transaction', methods=['POST'])
def update_transaction():
    client_decision = []

    # store the client_id, transaction_id and decision in a list of dictionary
    for client_transaction in request.form:
        temp = client_transaction.split("+")
        print(temp)
        """
        clientid=temp[0], transactionid=temp[1], transactiontype=temp[2], commissionpaid=temp[3], commissiontype=temp[4], 
        recipientid=temp[5], bitcoinamt=temp[6]
        """
        t = dict()
        t['client_id'] = temp[0]
        t['transaction_id'] = temp[1]
        t['transaction_type'] = temp[2]
        t['commission_paid'] = temp[3]
        t['commission_type'] = temp[4]
        t['recipient_id'] = temp[5]
        t['decision'] = "completed" if request.form[client_transaction]=="accept" else "reject"
        t['bitcoin_amt'] = temp[6]
        t['commission_rate_type'] = temp[7]
        client_decision.append(t)
    update_transaction_table(client_decision)

    return redirect(url_for('login'))

@app.route('/get_bit_rate',methods=['GET'])
def get_bit_rate():
    return json.dumps({'curr_rate':get_current_rate()})

## completed
@app.route('/buy_ether', methods=['POST'])
def buy_ether():
    obj = get_json_data(request.data)

    client_id = session["id"]
    bitcoin_unit_to_buy = float(obj["amt_to_buy"])
    curr_balance = float(obj["curr_bal"])
    curr_bitcoin = float(obj["curr_coin"])
    rate = float(get_current_rate())

    if bitcoin_unit_to_buy * rate < curr_balance:
        cursor = mysql.get_db().cursor()
        cursor.execute('UPDATE ACC_DETAILS SET FiatCurrency = %s WHERE ClientId = %s',
                       (curr_balance-(bitcoin_unit_to_buy*rate), client_id,))
        cursor.execute('UPDATE BITCOIN SET Units = %s WHERE ClientId = %s', (curr_bitcoin+bitcoin_unit_to_buy, client_id, ))
        mysql.get_db().commit()
        return json.dumps({"success":True, "msg":"Congratulations you just bought {} bitcoin from ether".format(bitcoin_unit_to_buy)})
    else :
        return json.dumps({"success":False, "msg":"Not enough money to buy from ether"})
