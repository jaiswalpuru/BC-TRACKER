import pymysql
import yaml
import datetime
import requests

with open("../config.yaml", "r") as stream:
    data_loaded = yaml.safe_load(stream)
config = data_loaded['DATABASE']


# get the current rate of bitcoin
def get_current_rate():
    response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
    return response.json()['bpi']['USD']['rate_float']


def job():
    conn = pymysql.connect(
        host='localhost',
        user = config['USERNAME'],
        password = config['PASSWORD'],
        db=config['DB'],
    )
    curr = conn.cursor()

    today = datetime.date.today()

    yesterday = today - datetime.timedelta(days=1)

    curr.execute('SELECT ClientId FROM Users')
    clients_data = curr.fetchall();

    for i in range(len(clients_data)):
        curr.execute('SELECT SUM(BitCoinAmount) FROM Transaction WHERE Date >= %s AND ClientId=%s', (yesterday,clients_data[i][0], ));
        tran_details = curr.fetchall()
        rate = get_current_rate()
        if tran_details[0][0] != None:
            if tran_details[0][0]*rate >= 100000:
                curr.execute('UPDATE USERS SET Type="GOLD" WHERE ClientId=%s',(clients_data[i][0],))
            else :
                curr.execute('UPDATE USERS SET Type="SILVER" WHERE ClientId=%s',(clients_data[i][0],))

    conn.commit()
    conn.close()

job()
