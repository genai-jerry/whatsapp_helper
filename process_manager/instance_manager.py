
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from xmlrpc.server import SimpleXMLRPCServer
from bs4 import BeautifulSoup
import os, requests
import qrcode, time
from persistent_driver import PersistentWebDriver
import threading

# URL for WhatsApp Web
whatsapp_web_url = "https://web.whatsapp.com/"
driver_path = 'driver/unzipped_contents/chromedriver-linux64/chromedriver'

browser_instances = {}
instances = {}

def store_instance(mobile_number, user_data):
    # Use mobile number as the key to store data in Redis
    # redis_client.set(user_data['mobile_number'], user_data)
    print('Storing Data')
    instances[mobile_number] = user_data
    print(f'Stored {instances}')

def update_instance(mobile_number, user_data):
    # Use mobile number as the key to store data in Redis
    # redis_client.set(user_data['mobile_number'], user_data)
    print('Storing Data')
    instance_data = instances[mobile_number]
    instance_data.update(user_data)
    print(f'Updated {instances}')

def retrieve_instance(mobile_number):
    # Retrieve JSON data from Redis using the mobile number as the key
    # return redis_client.get(mobile_number)
    print(f'Getting instance for {mobile_number}')
    instance = instances.get(mobile_number)
    print(f'Got instance {instance}')
    return instance

def get_all_instances():
    keys_to_exclude = []

    # Using list comprehension to map and filter
    print('Getting data from values')
    data = [{k: v for k, v in sub_dict.items()} for sub_dict in instances.values()]
    # Apply the function to the data
    print(f'Got data {data}')
    return data

def make_file_executable(file_path):
    # Get the current permissions
    current_permissions = os.stat(file_path).st_mode

    # Add executable permission to the owner
    new_permissions = current_permissions | 0o111

    # Set the new permissions
    os.chmod(file_path, new_permissions)

def refresh(mobile_number):
    try:
        browser = browser_instances[mobile_number]
        with browser.get_lock():
            browser.get_driver().refresh()
        return True
    except Exception as e:
        raise e
    
def create_instance(app_home, mobile_number):
    print('Creating instance')
    options = Options()
    options.add_argument("--headless=new")
    driver_file_path = os.path.join(app_home, driver_path)
    print(f'Driver path is {driver_file_path}. Making it executable')
    try:
        make_file_executable(driver_file_path)
        print('Loading chrome web driver')
        browser = webdriver.Chrome(executable_path=driver_file_path, options=options) 
        print('Getting the whatsapp web')
        browser.get(whatsapp_web_url)  

        if app_loaded(browser):
            persistent_browser = PersistentWebDriver(browser)
            print('Got the browser. Now keeping alive')
            my_thread = threading.Thread(target=persistent_browser.keep_alive)
            # Start the thread
            my_thread.start()
            browser_instances[mobile_number] = persistent_browser
            return True
        else:
            browser.quit()
            return False
    except Exception as e:
        raise e
    
def app_loaded(browser):
    print('Checking browser state')
    start_time = time.time()  # Record the start time
    timeout = 10  # Timeout in seconds

    while True:
        # Get the HTML of the page
        html = browser.page_source

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        # Find the element using BeautifulSoup and get the 'data-ref' attribute
        landing = soup.find('div', {"class":"landing-headerTitle"})
        if landing != None:
            print('Whatsapp loaded')
            return True
        if time.time() - start_time > timeout:
            print('Whatsapp not loaded')
            return False
        
    
def execute_script(function_name, mobile_number, script, variables):
    try:
        print('Executing the script')
        # Create a dictionary for local variables
        locals_dict = {}
        print('Getting browser instance')
        browser = browser_instances[mobile_number]
        print('Adding browser to arguments')
        variables.insert(0, browser.get_driver())
        # Execute the script in the context of locals_dict
        with browser.get_lock():
            exec(script, globals(), locals_dict)
        print('Executed')

        # Call the function named 'main' in the script and pass variables
        if function_name in locals_dict and callable(locals_dict[function_name]):
            print('Getting results from locals_dict')
            result = locals_dict[function_name](*variables)
            print('Returning result')
            return result
        else:
            return f"Function {function_name} not found or not callable in the script."
    except Exception as e:
        return f"Error executing script: {str(e)}"

if __name__ == "__main__":
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    server.register_function(execute_script, "execute_script")
    server.register_function(refresh, "refresh")
    server.register_function(create_instance, "create_instance")
    server.register_function(store_instance, "store_instance")
    server.register_function(update_instance, "update_instance")
    server.register_function(retrieve_instance, "retrieve_instance")
    server.register_function(get_all_instances, "get_all_instances")
    print("Server listening on port 8000...")
    server.serve_forever()