import logging
from pyicloud import PyiCloudService
from dotenv import load_dotenv
import os

print("Launching!")

def setupLogging():
    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger()
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)


api: PyiCloudService = None

def authenticate():
    # Load environment variables from .env file
    load_dotenv()

    USERNAME = os.getenv('ICLOUD_USERNAME')
    APP_SPECIFIC_PASSWORD = os.getenv('ICLOUD_APP_SPECIFIC_PASSWORD')

    try:
        api = PyiCloudService(USERNAME, APP_SPECIFIC_PASSWORD)
        print("Authentication successful!")
    except Exception as e:
        print(f"Authentication failed: {e}")
        exit(1)

    # Check if two-factor authentication is required
    if api.requires_2fa:
        import click
        print("Two-factor authentication required.")
        code = click.prompt('Please enter the code you received on your device')
        result = api.validate_2fa_code(code)
        print("Code validation result: %s" % result)

        if not result:
            print("Failed to verify security code")
            exit(1)

        if not api.is_trusted_session:
            print("Session is not trusted. Requesting trust...")
            result = api.trust_session()
            print("Session trust result %s" % result)

            if not result:
                print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")
    else:
        print("No two-factor authentication required")

    return api

setupLogging()
api = authenticate()
photos = api.photos.all.photos

firstPhoto = next(photos, None)

print("Downloading first photo...")
if firstPhoto:
    photo_name = firstPhoto.filename
    response = firstPhoto.download()

    if response.status_code == 200:
        # Get the raw photo data (bytes)
        photo_data = response.content
        
        home_directory = os.path.expanduser('~')
        file_path = os.path.join(home_directory, photo_name)

        with open(file_path, 'wb') as file:
            file.write(photo_data)
            print(f'Downloaded {photo_name} to {file_path}')

    else:
        # Handle failed request (e.g., 404 or 500)
        raise Exception(f"Failed to download photo. Status code: {response.status_code}")



    
   
else:
    print("No photos found.")

#  fetch_photos()