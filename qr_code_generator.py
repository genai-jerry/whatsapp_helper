from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import qrcode
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
import time
import os

# URL for WhatsApp Web
whatsapp_web_url = "https://web.whatsapp.com/"
driver_path = 'driver/unzipped_contents/chromedriver-linux64/chromedriver'
image_save_path = 'static/images'

def make_file_executable(file_path):
    # Get the current permissions
    current_permissions = os.stat(file_path).st_mode

    # Add executable permission to the owner
    new_permissions = current_permissions | 0o111

    # Set the new permissions
    os.chmod(file_path, new_permissions)

def create_instance(app_home):
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
        return browser
    except Exception as e:
        print(e)
        raise e

def load_qr_code(app_home, browser, host_number):
    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    while True:
        try:
            print('Waiting for qr_code')
            qr_div = browser.find_element_by_xpath('//div[@class="_19vUU"]')
            print('Page is ready!')
            start_time = time.time()  # Record the start time
            timeout = 30  # Timeout in seconds
            while True:
                try:
                    print('Waiting for data-ref')
                    # Get the canvas as a PNG base64 string
                    qr_div = browser.find_element_by_xpath('//div[@class="_19vUU"]')
                    data_ref = qr_div.get_attribute("data-ref")
                    if data_ref != None:
                        print(f'Got data {data_ref}')
                        qr.add_data(data_ref)
                        print('Fitting qr')
                        qr.make(fit=True)
                        print('Making Image')
                        # Create an image of the QR code
                        img = qr.make_image(fill_color="black", back_color="white")

                        # Save the QR code image to a file
                        image_path = os.path.join(app_home, image_save_path)
                        qr_file_path = f"{image_path}/whatsapp_web_qr_{host_number}.png"
                        print(f'Saving image to {qr_file_path}')
                        if os.path.exists(qr_file_path):
                            os.remove(qr_file_path)
                        img.save(qr_file_path)
                        return
                except Exception as e:
                    print(f'{e}')
                if time.time() - start_time > timeout:
                    raise RuntimeError('Unable to load QR Code')
                time.sleep(1)
        except:
            if time.time() - start_time > timeout:
                print('Loading took too much time!')
                raise RuntimeError('Unable to load QR Code')
