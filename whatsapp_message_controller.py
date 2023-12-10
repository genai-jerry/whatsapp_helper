from qr_code_generator import *
from whatsapp_automation import *

source_instances = {}
def create_and_send_message(source, destination, message, type):
    browser = source_instances.get(source)
    if browser == None:
        print('Creating new instance')
        browser = create_instance()
        source_instances[source] = browser
        scan_code(browser, source)
        return False
    
    print('Checking if the browser is ready')
    if is_instance_ready(browser):
        print('Sending message')
        if type == 1:
            send_whatsapp_message(browser, destination, message)
        else:
            send_video_whatsapp_message(browser, destination)
        return True
    else:
        print('Loading QR Code again')
        scan_code(browser, source)
        return False

def scan_code(browser, source):
    load_qr_code(browser, source)
    print('Please scan and activate the instance')
    while not is_instance_ready(browser):
        time.sleep(1)
    
def send_text_message(source, destination):
    message = input("Message to send: ")
    while not create_and_send_message(source, destination, message, 1):
        time.sleep(1)
    print(f"Message sent to {destination}: {message}")

def send_video_message(source, destination):
    while not create_and_send_message(source, destination, None, 2):
        time.sleep(1)
    print(f"Message sent to {destination}")

while True:
    source = '9900180339' #input("Please enter source number: ")
    destination = '9900180339' #input("Please enter destination: ")
    option = input("1. Text, 2. Video 2 : ")
    if option == '1':
        send_text_message(source, destination)
    else:
        send_video_message(source, destination)
   