import requests
import json

def add_lead(opportunity):
    # If the event is of type "VSL Shared", send a POST request to the external API
    url = "https://connect.pabbly.com/workflow/sendwebhookdata/IjU3NjUwNTY1MDYzNzA0MzI1MjY1NTUzNDUxM2Ii_pc"
    full_name = opportunity['name']
    name_parts = full_name.split()
    first_name = name_parts[0]
    last_name = name_parts[-1]
    data = {
        "Email": opportunity['email'],
        "First Name": first_name,
        "Last Name": last_name,
        "Phone": opportunity['phone'],
        "FBP": opportunity['fbp'],
        "FBC": opportunity['fbc']
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        print("Successfully sent data to external API")
    else:
        print("Failed to send data to external API")
        print(response.text)