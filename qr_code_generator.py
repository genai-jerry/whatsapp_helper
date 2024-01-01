import qrcode
import time
import os
from xmlrpc.client import ServerProxy
import inspect

# Connect to the server
server = ServerProxy("http://localhost:8000/", allow_none=True)

def load_qr_code(mobile_number, app_home):
    variables = (app_home, mobile_number)
    server.execute_script('__generate_qr_code', 
                                 mobile_number,inspect.getsource(__generate_qr_code), variables)
    
def __generate_qr_code(browser, app_home, host_number):
    print('Generating the QR Code')
    start_time = time.time()  # Record the start time
    timeout = 30  # Timeout in seconds
    image_save_path = 'static/images'
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
                        print(f'Storing QR code at {image_path}')
                        qr_file_path = f"{image_path}/whatsapp_web_qr_{host_number}.png"
                        print(f'Saving image to {qr_file_path}')
                        if os.path.exists(qr_file_path):
                            os.remove(qr_file_path)
                        img.save(qr_file_path)
                        return True
                except Exception as e:
                    print(f'{e}')
                if time.time() - start_time > timeout:
                    raise RuntimeError('Unable to load QR Code')
                time.sleep(1)
        except:
            if time.time() - start_time > timeout:
                print('Loading took too much time!')
                raise RuntimeError('Unable to load QR Code')
