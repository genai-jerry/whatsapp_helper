from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import os, requests
from xmlrpc.client import ServerProxy
import inspect
from store.message_store import *
import threading

# Connect to the server
server = ServerProxy("http://localhost:8000/", allow_none=True)
# Create a lock to synchronize access to a resource
resource_lock = threading.Lock()
browser_instance_locks = {}
# Function to send a WhatsApp message
def is_instance_ready(mobile_number):
    if server.instance_exists(mobile_number):
        state = server.execute_script('__check_browser_state', 
                                    mobile_number,inspect.getsource(__check_browser_state), [])
        print(f'Instance is {state}')
        return state
    else:
        raise Exception

def obtain_sender_lock(sender):
    lock = None
    if sender in browser_instance_locks:
        lock = browser_instance_locks[sender]
    if lock == None:
        with resource_lock:
            lock = threading.Lock()
            browser_instance_locks[sender] = lock
    return lock
    
# Function to send a WhatsApp message
def send_whatsapp_message(message_data):
    print('Setting up message box')
    sender = message_data['sender']
    receiver = message_data['receiver']
    message = message_data['message']
    id = message_data['id']
    try:
        with obtain_sender_lock(sender):
            variables_1 = [receiver]
            result = server.execute_script('__setup_contact_message_box', sender, 
                                        inspect.getsource(__setup_contact_message_box)
                                , variables_1)
            print(f'Executed and got result {result}')
            start_time = time.time()  # Record the start time
            timeout = 30  # Timeout in seconds

            variables_2 = [message]
            while not server.execute_script('__send_message', sender,
                                inspect.getsource(__send_message), variables_2):
                if time.time() - start_time > timeout:
                    raise RuntimeError('Unable to send message')
                time.sleep(1)
            update_message(id, 'Sent', None)
    except Exception as e:
        update_message(id, 'Error', str(e)[:255])
        print(f'Caught {e}')

# Function to send a WhatsApp message
def send_media_whatsapp_message(message_data):
    sender = message_data['sender']
    receiver = message_data['receiver']
    app_home = message_data['app_home']
    file_url = message_data['message']
    id = message_data['id']
    variables_1 = [receiver]
    
    try:
        with obtain_sender_lock(sender):
            server.execute_script('__setup_contact_message_box', sender,
                            inspect.getsource(__setup_contact_message_box), variables_1)
            start_time = time.time()  # Record the start time
            timeout = 30  # Timeout in seconds

            print('Attaching Media for sending file')
            variables_2 = [app_home, file_url]
            attached = server.execute_script('__attach_media', sender,
                                inspect.getsource(__attach_media), variables_2)
            print(f'Attached {attached}')
            while not attached:
                if time.time() - start_time > timeout:
                    raise RuntimeError('Unable to send media message')
                time.sleep(1)
                attached = server.execute_script('__attach_media', sender,
                                inspect.getsource(__attach_media), variables_2)

            start_time = time.time()  # Record the start time
            timeout = 30  # Timeout in seconds

            while not server.execute_script('__send_media', sender,
                                inspect.getsource(__send_media), []):
                if time.time() - start_time > timeout:
                    raise RuntimeError('Unable to send media message')
                time.sleep(1)
            update_message(id, 'Sent', None)
    except Exception as e:
        update_message(id, 'Error', str(e)[:255])
        print(e)

def __check_browser_state(browser):
    print('Checking browser state')
    # Get the HTML of the page
    html = browser.page_source

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # Find the element using BeautifulSoup and get the 'data-ref' attribute
    profile = soup.find('div', {"aria-label":"profile photo"})
    print(f'Profile is {profile}')
    return profile != None


def __attach_media(browser, app_home, file_url):
    print('Attaching the file')
    media_home = 'static/media/'
    def __attach_media_file(media_path, browser, file_name):
        print('Attaching media file')
        attach_link = browser.find_element("xpath",'//*[@title="Attach"]')
        attach_link.click()

        # Locate the file input element (assuming it's hidden)
        file_input = browser.find_element("xpath",'//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime" and @type="file" and @multiple="" and @style="display: none;"]')
        file_path = f'{media_path}{file_name}'
        # Send the file path to the now-visible input element
        print('Sending attached file')
        file_input.send_keys(os.path.abspath(file_path))

    def __download_file(url, destination_folder):
        # Make a request to the URL
        print('Downloading file')
        response = requests.get(url, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            # Extract filename from URL
            filename = url.split('/')[-1]

            # Create the full path for the destination
            destination_file_path = destination_folder + '/' + filename
            print(f'Storing file at {destination_file_path}')
            # Open a file with the same name in binary write mode
            with open(destination_file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=128):
                    file.write(chunk)

            return filename
        else:
            print(f"Error downloading file: {response.status_code}")
            raise RuntimeError("Unable to download the file.")
    media_path = os.path.join(app_home, media_home)
    file_name = __download_file(file_url, media_path)
    __attach_media_file(media_path, browser, file_name)
    return True

def __send_media(browser):
    try:
        print('Sending file')
        send_button = browser.find_element("xpath",'//div[@role="button" and @aria-label="Send"]')
        send_button.click()
        return True
    except:
        return False

def __send_message(browser, message):
    print('Clicking to write the message')
    message_box = browser.find_element("xpath",'//*[@title="Type a message"]')
    message_box.click()
    message_box.send_keys(message)
    message_box.send_keys(Keys.ENTER)
    print('Sending message to contact')
    return True

def __setup_contact_message_box(browser, contact_name):
    print('Opening New Chat')
    def __open_new_chat(browser):
        print('Opening new chat')
        new_chat = browser.find_element("xpath",'//*[@aria-label="New chat"]')
        print('Clicking to start')
        new_chat.click()
        print('Ready to chat')
        return True
    
    def __search_and_start_chat(browser, contact_name):
        print('Opening Search Box')
        search_box = browser.find_element("xpath",'//*[@title="Search input textbox"]')
        search_box.click()
        print('Searching for the contact')
        search_box.send_keys(contact_name)
        time.sleep(1)
        print('Message box for contact opened')
        return True
    
    def __load_contact_message_box(browser):
        # //div[contains(text(), 'Contacts on WhatsApp')]/ancestor::div[@role='listitem'][1]/following-sibling::div[@role='listitem']
        # //div[contains(text(), 'Not in your contacts')]/following-sibling::div[1]
        try:
            print('Check contact in WhatsApp')
            contact_item = browser.find_element("xpath","//div[contains(text(), 'Contacts on WhatsApp')]/ancestor::div[@role='listitem'][1]/following-sibling::div[@role='listitem']")
            contact_item.click()
            return True
        except Exception as e:
            try:
                print(e)
                contact_item = browser.find_element("xpath","//div[contains(text(), 'Not in your contacts')]/following-sibling::div[1]")
                contact_item.click()
                return True
            except:
                print('Contact not on WhatsApp')
                return False
            
    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    print('Opening New Chat')
    while not __open_new_chat(browser):
        if time.time() - start_time > timeout:
            raise RuntimeError('Unable to open new chat')
        time.sleep(1)

    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    while not __search_and_start_chat(browser, contact_name):
        if time.time() - start_time > timeout:
            raise RuntimeError('Unable to send message')
        time.sleep(1)

    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    while not __load_contact_message_box(browser):
        if time.time() - start_time > timeout:
            raise RuntimeError('Unable to find contact')
        time.sleep(1)

# Function to handle the callback when the div changes
def __handle_div_change(message):
    print("Chat List content changed:", message)


