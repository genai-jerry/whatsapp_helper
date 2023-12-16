from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import os, requests
from selenium.webdriver.common.by import By

media_home = './static/media/'
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
    new_chat = browser.find_element_by_xpath('//*[@aria-label="New chat"]')
    print('Clicking to start')
    new_chat.click()
    print('Ready to chat')
    return True

def attach_media_file(browser, file_name):
    attach_link = browser.find_element_by_xpath('//*[@title="Attach"]')
    attach_link.click()

    # Locate the file input element (assuming it's hidden)
    file_input = browser.find_element_by_xpath('//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime" and @type="file" and @multiple="" and @style="display: none;"]')

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

def attach_media(browser, file_url):
    print('Attaching the file')
    file_name = download_file(file_url, media_home)
    attach_media_file(browser, file_name)
    return True

def send_media(browser):
    try:
        send_button = browser.find_element_by_xpath('//div[@role="button" and @aria-label="Send"]')
        send_button.click()
        return True
    except:
        return False

def load_contact_message_box(browser):
    # //div[contains(text(), 'Contacts on WhatsApp')]/ancestor::div[@role='listitem'][1]/following-sibling::div[@role='listitem']
    # //div[contains(text(), 'Not in your contacts')]/following-sibling::div[1]
    try:
        print('Check contact in WhatsApp')
        contact_item = browser.find_element_by_xpath("//div[contains(text(), 'Contacts on WhatsApp')]/ancestor::div[@role='listitem'][1]/following-sibling::div[@role='listitem']")
        contact_item.click()
        return True
    except Exception as e:
        try:
            print(e)
            contact_item = browser.find_element_by_xpath("//div[contains(text(), 'Not in your contacts')]/following-sibling::div[1]")
            contact_item.click()
            return True
        except:
            print('Contact not on WhatsApp')
            return False
        
def search_and_start_chat(browser, contact_name):
    print('Opening Search Box')
    search_box = browser.find_element_by_xpath('//*[@title="Search input textbox"]')
    search_box.click()
    print('Searching for the contact')
    search_box.send_keys(contact_name)
    time.sleep(1)
    print('Message box for contact opened')
    return True

def send_message(browser, message):
    print('Clicking to write the message')
    message_box = browser.find_element_by_xpath('//*[@title="Type a message"]')
    message_box.click()
    message_box.send_keys(message)
    message_box.send_keys(Keys.ENTER)
    print('Sending message to contact')
    return True

def setup_contact_message_box(browser, contact_name):
    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    while not open_new_chat(browser):
        if time.time() - start_time > timeout:
            raise RuntimeError('Unable to open new chat')
        time.sleep(1)

    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    while not search_and_start_chat(browser, contact_name):
        if time.time() - start_time > timeout:
            raise RuntimeError('Unable to send message')
        time.sleep(1)

    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    while not load_contact_message_box(browser):
        if time.time() - start_time > timeout:
            raise RuntimeError('Unable to find contact')
        time.sleep(1)

# Function to send a WhatsApp message
def send_whatsapp_message(browser, contact_name, message):
    setup_contact_message_box(browser, contact_name)

    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    while not send_message(browser, message):
        if time.time() - start_time > timeout:
            raise RuntimeError('Unable to send message')
        time.sleep(1)

# Function to send a WhatsApp message
def send_media_whatsapp_message(browser, contact_name, file_url):
    setup_contact_message_box(browser, contact_name)
    
    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    while not attach_media(browser, file_url):
        if time.time() - start_time > timeout:
            raise RuntimeError('Unable to send media message')
        time.sleep(1)

    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    while not send_media(browser):
        if time.time() - start_time > timeout:
            raise RuntimeError('Unable to send media message')
        time.sleep(1)