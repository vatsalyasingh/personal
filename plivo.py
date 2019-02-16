import requests
import json
import sys
from requests.auth import HTTPBasicAuth

# Calls Plivo Numbers API
# API calls needs to be authenticated using HTTPBasicAuth
# AUTH_ID and AUTH_TOKEN needs to be sent for Basic Authentication
# After receiving the API response, find out the two numbers from API Response
# Returns first two numbers from the response
def get_numbers():
    """
    {
        "api_id": "60ce9d7a-31b0-11e9-8364-0233ac9f50b4",
        "meta": {
            "limit": 20,
            "next": null,
            "offset": 0,
            "previous": null,
            "total_count": 2
        },
        "objects": [
            {
                "active": true,
                "application": "/v1/Account/MAODUZYTQ0Y2FMYJBLOW/Application/33829815390645281/",
                "carrier": "Plivo",
                "country": "United States",
                "monthly_rental_rate": "0.80000",
                "number": "14158408589",
            },
            {
                "active": true,
                "application": "/v1/Account/MAODUZYTQ0Y2FMYJBLOW/Application/33828651528937946/",
                "carrier": "Plivo",
                "city": null,
                "country": "United States",
                "monthly_rental_rate": "0.80000",
                "number": "14158408583",
        ]
    }
    """
    print("Getting numbers")
    url = "https://api.plivo.com/v1/Account/" + auth_id + "/Number/"
    response = requests.request("GET", url, auth=HTTPBasicAuth(auth_id, auth_token))
    if response.status_code == 200:
        data = json.loads(response.text)
        objects = data["objects"]
        if objects:
            return objects[0]["number"], objects[1]["number"]
    else:
        print(response.text)
        print("Fail")
        sys.exit()

# Sends Message using Plivo API
# API calls needs to be authenticated using HTTPBasicAuth
# AUTH_ID and AUTH_TOKEN needs to be sent for Basic Authentication
# Parameters:
#   src -> from number
#   dst -> to number
#   text -> Message to send
# Response:
#   message_uuid
# After receiving the API response,
# It Returns message_uuid from the response
def send_message(src,dst):
    """
    {
        "api_id": "c4d98426-31ae-11e9-ac27-0651e9348e2e",
        "message": "message(s) queued",
        "message_uuid": [
            "c4d9e524-31ae-11e9-ac27-0651e9348e2e"
        ]
    }
    """
    print("Sending Message")
    url = "https://api.plivo.com/v1/Account/" + auth_id + "/Message/"
    payload = { "src": src, "dst": dst, "text": "TEST_MESSAGE" }
    response = requests.request("POST", url, data=payload, auth=HTTPBasicAuth(auth_id, auth_token))
    data = json.loads(response.text)
    if response.status_code == 202:
        return data["message_uuid"][0]
    else:
        print(response.text)
        print("Fail")
        sys.exit()

# Gets details of the Message using Plivo API
# API calls needs to be authenticated using HTTPBasicAuth
# AUTH_ID and AUTH_TOKEN needs to be sent for Basic Authentication
# Parameters:
#   Message UUID will be passed to the API
# Response:
#   Details of the message along with message status
# Returns Total Amount Charged for sending this message
def get_message_details(uuid):
    """
    {
        "api_id": "d5564ac8-31ae-11e9-ac87-0625cd561840",
        "error_code": "900",
        "from_number": "14158408589",
        "message_direction": "outbound",
        "message_state": "failed",
        "message_time": "2019-02-16 11:20:30+05:30",
        "message_type": "sms",
        "message_uuid": "c4d9e524-31ae-11e9-ac27-0651e9348e2e",
        "resource_uri": "/v1/Account/MAODUZYTQ0Y2FMYJBLOW/Message/c4d9e524-31ae-11e9-ac27-0651e9348e2e/",
        "to_number": "14158408583",
        "total_amount": "0.00000",
        "total_rate": "0.00000",
        "units": 1
    }
    """
    print("Getting Message Details")
    url = "https://api.plivo.com/v1/Account/" + auth_id + "/Message/" + uuid
    response = requests.request("GET", url, auth=HTTPBasicAuth(auth_id, auth_token))
    data = json.loads(response.text)
    if response.status_code == 200:
        if data["message_state"] == "sent":
            return data["total_amount"]
        else:
            print(response.text)
            print("Fail")
            sys.exit()
    else:
        print(response.text)
        print("Fail")
        sys.exit()

# Gets Price details of the country using Plivo API
# API calls needs to be authenticated using HTTPBasicAuth
# AUTH_ID and AUTH_TOKEN needs to be sent for Basic Authentication
# Parameters:
#   Country Code needs to be passed
# Response:
#   Price Chart defined for that country is returned
# Returns Amount Defined for sending Outbound SMS
def get_country_price_details(code):
    """
    {
        "api_id": "bec96c28-31a8-11e9-96d8-066208d1cfdc",
        "country": "United States",
        "country_code": 1,
        "country_iso": "US",
        "message": {
            "inbound": {
                "rate": "0.00000"
            },
            "outbound": {
                "rate": "0.00350"
            },
        }
    }
    """
    print("Getting Country Price Details")
    url = "https://api.plivo.com/v1/Account/" + auth_id + "/Pricing/"
    querystring = {"country_iso": code}
    response = requests.request("GET", url, params=querystring, auth=HTTPBasicAuth(auth_id, auth_token))
    data = json.loads(response.text)
    if response.status_code == 200:
        return data["message"]["outbound"]["rate"]
    else:
        print(response.text)
        print("Fail")
        sys.exit()

auth_id = input("Enter Auth ID:")
auth_token = input("Enter Auth token:")

# Get the numbers
src, dst = get_numbers()

# When SOURCE NUMBER and DESTINATION NUMBER is identified
# Send Message from SRC Number to DST Number
if src and dst:
    uuid = send_message(src,dst)
else:
    print("Fail")
    sys.exit()

# When Message is queued for sending
# Check Details of the message
if uuid:
    total_amount = get_message_details(uuid)
else:
    print("Fail")
    sys.exit()

# Get Price chart for this country
expected_price = get_country_price_details("US")

# Check if amount deducted is same as the amount defined for that country
if total_amount == expected_price:
    print("Pass")
else:
    print("Fail")
