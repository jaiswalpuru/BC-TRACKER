import json

# returns the dictionary from byte string
def get_json_data(req):
    bytes_response = req
    json_response = bytes_response.decode('utf8').replace("'", '"')
    obj = json.loads(json_response)
    return obj
