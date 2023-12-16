import requests
import os
import re
from urllib.request import urlretrieve
import zipfile

# Configuration
platform = 'linux64'  # Change this to 'win32', 'mac64', or 'linux64' as needed
storage_dir = './driver'  # Change to your desired directory

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
    unzip_zip_file(storage_dir)

def unzip_zip_file(directory_path):
    # Get the list of files in the specified directory
    file_list = os.listdir(directory_path)

    # Look for a zip file in the directory
    zip_file = None
    for file in file_list:
        if file.endswith('.zip'):
            zip_file = file
            break

    if zip_file:
        zip_file_path = os.path.join(directory_path, zip_file)
        target_folder = os.path.join(directory_path, 'unzipped_contents')

        # Create the target folder if it doesn't exist
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # Extract the contents of the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(target_folder)

        print(f'Successfully extracted contents from {zip_file} to {target_folder}')
    else:
        print('No zip file found in the specified directory.')

