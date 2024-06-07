import json
from selenium.webdriver.common.keys import Keys
import time
import requests
from store.message_store import *
from store.instance_store import retrieve_instance

# Connect to the server
url = "https://wa.smsidea.com/api/v1/GetConnectionStatus"

def is_whatsapp_ready(mobile_number):
    instance = retrieve_instance(mobile_number)
    if instance == None:
        return False
    else:
        params = {
            'key': instance['sms_idea_api_key']
        }
        print('Requesting instance state')
        response = requests.get(url, params=params)
        data = response.json()
        print('QR code response:', data)
        if data['ErrorCode'] == '000':
            if data['Data']['Status'] == 'CONNECTED':
                return True
            else:
                return False
        else:
            print('Error:', data['ErrorMessage'])
            return False
    

def refresh_browser(mobile_number):
    return True

# Function to send a WhatsApp message
def is_instance_ready(mobile_number):
    instance = retrieve_instance(mobile_number)
    if instance == None:
        return False
    if instance['status'] == 'Ready':
        return True
    else:
        return False
    
# Function to send a WhatsApp message
def send_whatsapp_message(message_data):
    sender = message_data['sender']
    receiver = message_data['receiver']
    message = message_data['message']
    id = message_data['id']
    # Get the message status
    status = retrieve_message_by_id(id)
    print('Sending whatsapp message')
    # Check if the status is "Abandon"
    if status['status'] == "Abandon":
        # Update message status to "Abandoned"
        print(f'Abandoning {id}')
        update_message(id, "Abandoned", None)
        return

    # Continue with the rest of the code

    url = "https://wa.smsidea.com/api/v1/sendMessage"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'key': "1100bb7ba3964ac4af097202c831cd67",
        'to': receiver,
        'message': message
    }
    try:
        print(f'Sending Message with Data {data}')
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f'Response {response}')
        response.raise_for_status()
        print(f'Message sent to {receiver}, updating id {id} to Sent')
        update_message(id, 'Sent', None)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
        update_message(id, 'Error', str(errh)[:255])
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
        update_message(id, 'Error', str(errc)[:255])
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
        update_message(id, 'Error', str(errt)[:255])
    except requests.exceptions.RequestException as err:
        print ("Something went wrong",err) 
        update_message(id, 'Error', str(err)[:255])
   

# Function to send a WhatsApp message
def send_media_whatsapp_message(message_data):
    sender = message_data['sender']
    receiver = message_data['receiver']
    app_home = message_data['app_home']
    file_url = message_data['message']
    id = message_data['id']
    variables_1 = [receiver]
    
    update_message(id, 'Error', str(e)[:255])
    time.sleep(5)
    send_media_whatsapp_message(message_data)


