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
# Create a QR code instance
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
driver_path = 'driver/unzipped_contents/chromedriver-linux64/chromedriver'
image_save_path = 'static/media'

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
    try:
        print('Waiting for qr_code')
        WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div._19vUU')))
        print('Page is ready!')
    except TimeoutException:
        print('Loading took too much time!')
        return

    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    while True:
        # Get the HTML of the page
        html = browser.page_source

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        try:
            # Find the element using BeautifulSoup and get the 'data-ref' attribute
            divs = soup.find('div', {"class":"_19vUU"})

            if divs != None:
                print('Waiting for data-ref')
                # Get the canvas as a PNG base64 string
                data_ref = divs.attrs["data-ref"]
                qr.add_data(data_ref)
                qr.make(fit=True)

                # Create an image of the QR code
                img = qr.make_image(fill_color="black", back_color="white")

                # Save the QR code image to a file
                image_path = os.path.join(app_home, image_save_path)
                img.save(f"{image_path}/whatsapp_web_qr_{host_number}.png")

                return 
        
        except Exception as e:
            print(f'{e}')
            
        if time.time() - start_time > timeout:
            raise RuntimeError('Unable to send message')
