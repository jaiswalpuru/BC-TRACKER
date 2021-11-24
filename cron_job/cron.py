import schedule
import time
import pymysql
import yaml

with open("config.yaml", "r") as stream:
    data_loaded = yaml.safe_load(stream)
config = data_loaded['DATABASE']

schedule.every().day.at("10:30").do(job)

def job():
    conn = pymysql.connect(
        host='localhost',
        user = config['USERNAME'],
        password = config['PASSWORD'],
        db=config['DB'],
    )
    curr = conn.cursor()

    #do some work
    # 1. Fetch all the transaction for all the clients
    # 2. For each client fetch all the transaction for the past one day and check if the transaction has
    # exceeded $100k, if it has then upgrade the user to gold member, if the total number of transaction for the last day
    # was less than $100K then either degrade the user to silver if he is a gold member already or leave it as it is

    conn.close()

while True:
    schedule.run_pending()
