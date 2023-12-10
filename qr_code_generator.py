from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import qrcode
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

# URL for WhatsApp Web
whatsapp_web_url = "https://web.whatsapp.com/"
# Create a QR code instance
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
driver_path = '/home/jerrykurian/Public/code/whatsapp_helper/driver/chromedriver-linux64/chromedriver'
image_save_path = '/home/jerrykurian/Public/code/whatsapp_helper/img'
def create_instance():
    options = Options()
    options.add_argument("--headless=new")
    browser = webdriver.Chrome(executable_path=driver_path) 
    print('Getting the whatsapp web')
    browser.get(whatsapp_web_url)  
    return browser

def load_qr_code(browser, host_number):
    try:
        print('Waiting for qr_code')
        WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div._19vUU')))
        print('Page is ready!')
    except TimeoutException:
        print('Loading took too much time!')

    while True:
        try:
            # Get the HTML of the page
            html = browser.page_source

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
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
                img.save(f"{image_save_path}/whatsapp_web_qr_{host_number}.png")

                return 
        except Exception as e:
            print(f'{e}')
