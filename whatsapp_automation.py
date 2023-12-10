from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import os
from selenium.webdriver.common.by import By

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

def attach_file(browser):
    # Locate the file input element (assuming it's hidden)
    file_input = browser.find_element(By.CSS_SELECTOR, "input[type='file']")
    # Make the file input element visible using JavaScript
    browser.execute_script("arguments[0].style.display = 'block';", file_input)
    file_path = '/home/jerrykurian/amit-standing.jpeg'
    # Send the file path to the now-visible input element
    file_input.send_keys(os.path.abspath(file_path))

def send_video(browser):
    print('Attaching the file')
    attach_file(browser)
    while True:
        try:
            print('Sending file')
            send_button = browser.find_element_by_xpath('//*[@aria-label="Send"]')
            send_button.click()
            print('File sent')
            return True
        except:
            time.sleep(1)
    
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
    try:
        while not search_and_start_chat(browser, contact_name):
            time.sleep(1)
        while not send_message(browser, message):
            time.sleep(1)
    except Exception as e:
        print(f"Failed to send message: {e}")

# Function to send a WhatsApp message
def send_video_whatsapp_message(browser, contact_name):
    try:
        while not search_and_start_chat(browser, contact_name):
            time.sleep(1)
        while not send_video(browser):
            time.sleep(1)
    except Exception as e:
        print(f"Failed to send message: {e}")
