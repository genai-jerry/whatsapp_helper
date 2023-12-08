from qr_code_generator import *
from whatsapp_automation import *

source_instances = {}
def send_message(source, destination, message):
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
        send_whatsapp_message(browser, destination, message)
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
    
source_number = '9900180339'
while True:
    destination = input("Please enter destination: ")
    message = input("Message to send: ")
    while not send_message(source_number, destination, message):
        time.sleep(1)
    
    print(f"Message sent to {destination}: {message}")