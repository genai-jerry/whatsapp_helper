import requests
import os
import re
from urllib.request import urlretrieve

# Configuration
platform = 'linux64'  # Change this to 'win32', 'mac64', or 'linux64' as needed
storage_dir = '/home/jerrykurian/Public/code/whatsapp_helper/driver'  # Change to your desired directory

# Fetch the latest Chrome driver information
def get_latest_driver_info():
    url = 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json'
    response = requests.get(url)
    data = response.json()
    
    stable_version_info = data['channels']['Stable']
    version = stable_version_info['version']
    download_url = None

    for chrome_info in stable_version_info['downloads']['chromedriver']:
        if chrome_info['platform'] == platform:
            download_url = chrome_info['url']
            break

    return version, download_url

# Download and save the driver
def download_driver(download_url, version):
    file_name = f'chromedriver_{version}.zip'
    file_path = os.path.join(storage_dir, file_name)
    urlretrieve(download_url, file_path)
    print(f'Downloaded ChromeDriver version {version} to {file_path}')

# Check and update Chrome driver
def update_chrome_driver():
    latest_version, download_url = get_latest_driver_info()

    # Check if the driver file already exists
    existing_files = os.listdir(storage_dir)
    version_pattern = re.compile(r'chromedriver_(\d+\.\d+\.\d+\.\d+)\.zip')

    for file in existing_files:
        match = version_pattern.match(file)
        if match and match.group(1) == latest_version:
            print(f'Latest ChromeDriver version {latest_version} is already downloaded.')
            return

    # Download the latest version
    download_driver(download_url, latest_version)

# Run the update check
update_chrome_driver()
