import requests
import base64
import os
import configparser

config = configparser.ConfigParser()
config.read('config/config.ini')

# Connect to the server
url = "https://wa.smsidea.com/api/v1/GetQRCode"
def load_qr_code(mobile_number, app_home):
    try:
        print('Generating QR code from SMS Idea')
        params = {
            'masterkey': config.get('smsidea', 'masterkey')
        }
        print('Requesting QR code')
        response = requests.get(url, params=params)
        data = response.json()
        print('QR code response:', data)
        if data['ErrorCode'] == '000':
            image_data = data['Data']['QRBase64'].split(',')[1]
            image_save_path = 'static/images'
            image_path = os.path.join(app_home, image_save_path)
            qr_file_path = f"{image_path}/whatsapp_web_qr_{mobile_number}.png"
            if os.path.exists(qr_file_path):
                os.remove(qr_file_path)
            with open(qr_file_path, 'wb') as f:
                f.write(base64.b64decode(image_data))
            api_key = data['Data']['ApiKey']
            print(f'QR code saved as {qr_file_path} with API {api_key}')
            return api_key
        else:
            print('Error:', data['ErrorMessage'])
            return None
    except Exception as e:
        print('Error:', str(e))
        return None