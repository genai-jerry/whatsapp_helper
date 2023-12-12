from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import os, requests
from selenium.webdriver.common.by import By

media_home = '/home/jerrykurian/Public/code/whatsapp_helper/static/videos/'
# Function to send a WhatsApp message
def is_instance_ready(browser):
    # Get the HTML of the page
    html = browser.page_source

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # Find the element using BeautifulSoup and get the 'data-ref' attribute
    profile = soup.find('div', {"aria-label":"profile photo"})
    return profile != None

def load_html(browser):
    # Get the HTML of the page
    html = browser.page_source
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def open_new_chat(browser):
    print('Opening new chat')
    soup = load_html(browser)
    # Locate the New Chat icon and click
    new_chat = soup.find('div', {'aria-label':'New chat'})
    print(f'new chat is {new_chat}')
    if new_chat is None:
        return False
    else:
        print('Clicking to start')
        new_chat = browser.find_element_by_xpath('//*[@aria-label="New chat"]')
        new_chat.click()
        print('Ready to chat')
        return True

def attach_file(browser, file_name):
    # Locate the file input element (assuming it's hidden)
    file_input = browser.find_element(By.CSS_SELECTOR, "input[type='file']")
    # Make the file input element visible using JavaScript
    browser.execute_script("arguments[0].style.display = 'block';", file_input)
    file_path = f'{media_home}{file_name}'
    # Send the file path to the now-visible input element
    file_input.send_keys(os.path.abspath(file_path))

def download_file(url, destination_folder):
    # Make a request to the URL
    response = requests.get(url, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract filename from URL
        filename = url.split('/')[-1]

        # Create the full path for the destination
        destination_file_path = destination_folder + '/' + filename

        # Open a file with the same name in binary write mode
        with open(destination_file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)

        return filename
    else:
        print(f"Error downloading file: {response.status_code}")
        raise RuntimeError("Unable to download the file.")

def send_media(browser, file_url):
    print('Attaching the file')
    file_name = download_file(file_url, media_home)
    attach_file(browser, file_name)
    try:
        print('Sending file')
        send_button = browser.find_element_by_xpath('//*[@aria-label="Send"]')
        send_button.click()
        print('File sent')
        return True
    except:
        return False
    
def search_and_start_chat(browser, contact_name):
    print('Searching the contact')
    soup = load_html(browser)
    # Locate the search input field
    search_box = soup.find('div', {'title': 'Search input textbox'})
    if search_box == None:
        return False
    else:
        print('Clicking to enter details')
        search_box = browser.find_element_by_xpath('//*[@title="Search input textbox"]')
        search_box.click()
        search_box.send_keys(contact_name)
        search_box.send_keys(Keys.ENTER)
        print('Message box for contact opened')
        return True

def send_message(browser, message):
    print('Sending message')
    soup = load_html(browser)
    # Send message in the message box
    message_box = soup.find('div', {"title": "Type a message"})
    if message_box == None:
        return False
    else:
        print('Clicking to write the message')
        message_box = browser.find_element_by_xpath('//*[@title="Type a message"]')
        message_box.click()
        message_box.send_keys(message)
        message_box.send_keys(Keys.ENTER)
        print('Sending message to contact')
        return True

# Function to send a WhatsApp message
def send_whatsapp_message(browser, contact_name, message):
    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    while not search_and_start_chat(browser, contact_name):
        if time.time() - start_time > timeout:
            raise RuntimeError('Unable to send message')
        time.sleep(1)

    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    while not send_message(browser, message):
        if time.time() - start_time > timeout:
            raise RuntimeError('Unable to send message')
        time.sleep(1)

# Function to send a WhatsApp message
def send_media_whatsapp_message(browser, contact_name, file_url):
    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    while not search_and_start_chat(browser, contact_name):
        if time.time() - start_time > timeout:
            raise RuntimeError('Unable to send message')
        time.sleep(1)

    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    while not send_media(browser, file_url):
        if time.time() - start_time > timeout:
            raise RuntimeError('Unable to send message')
        time.sleep(1)
