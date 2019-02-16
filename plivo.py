import requests
import json
import sys
from requests.auth import HTTPBasicAuth

def get_numbers():
    print("Getting numbers")
    url = "https://api.plivo.com/v1/Account/" + auth_id + "/Number/"
    response = requests.request("GET", url, auth=HTTPBasicAuth(auth_id, auth_token))
    data = json.loads(response.text)
    if response.status_code == 200:
        objects = data["objects"]
        if objects:
            return objects[0]["number"], objects[1]["number"]
    else:
        print("Fail")
        sys.exit()

def send_message(src,dst):
    print("Sending Message")
    url = "https://api.plivo.com/v1/Account/" + auth_id + "/Message/"
    payload = { "src": src, "dst": dst, "text": "TEST_MESSAGE" }
    response = requests.request("POST", url, data=payload, auth=HTTPBasicAuth(auth_id, auth_token))
    data = json.loads(response.text)
    if response.status_code == 202:
        return data["message_uuid"][0]
    else:
        print("Fail")
        sys.exit()

def get_message_details(uuid):
    print("Getting Message Details")
    url = "https://api.plivo.com/v1/Account/" + auth_id + "/Message/" + uuid
    response = requests.request("GET", url, auth=HTTPBasicAuth(auth_id, auth_token))
    data = json.loads(response.text)
    if response.status_code == 200:
        if data["message_state"] == "sent":
            return data["total_amount"]
        else:
            print("Fail")
            sys.exit()
    else:
        print("Fail")
        sys.exit()

def get_country_price_details(code):
    print("Getting Country Price Details")
    url = "https://api.plivo.com/v1/Account/" + auth_id + "/Pricing/"
    querystring = {"country_iso": code}
    response = requests.request("GET", url, params=querystring, auth=HTTPBasicAuth(auth_id, auth_token))
    data = json.loads(response.text)
    if response.status_code == 200:
        return data["message"]["outbound"]["rate"]
    else:
        print("Fail")
        sys.exit()

auth_id = input("Enter Auth ID:")
auth_token = input("Enter Auth token:")
src, dst = get_numbers()

# When SOURCE NUMBER and DESTINATION NUMBER is identified
if src and dst:
    uuid = send_message(src,dst)
else:
    print("Fail")
    sys.exit()

# When Message is queued for sending
if uuid:
    total_amount = get_message_details(uuid)
else:
    print("Fail")
    sys.exit()

expected_price = get_country_price_details("US")

if total_amount == expected_price:
    print("Pass")
else:
    print("Fail")
