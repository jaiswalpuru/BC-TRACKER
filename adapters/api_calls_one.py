import requests

# get the current rate of bitcoin
def get_current_rate():
    response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
    return response.json()['bpi']['USD']['rate_float']
