import json
import datetime
import random
import string

# returns the dictionary from byte string
def get_json_data(req):
    bytes_response = req
    json_response = bytes_response.decode('utf8').replace("'", '"')
    obj = json.loads(json_response)
    return obj

# get the tax rate based on the type of the user
def get_tax_rate(val):
    # tax rate based on membership type
    tax_rate_gold_member = 5.0
    tax_rate_silver_member = 7.0
    if val == 'gold':
        return tax_rate_gold_member
    return tax_rate_silver_member

# return the current date time as per the specification of the db
def get_current_datetime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# return random string
def get_random_string():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))