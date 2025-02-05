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


def fetch_photos():
    # Get the most recent 10 photos

    # TypeError: 'PhotoAlbum' object is not subscriptable
    photos = api.photos.all
    recent_photos = photos[:10]

    # Create a directory to save the photos
    os.makedirs('downloaded_photos', exist_ok=True)

    # Download the photos
    for photo in recent_photos:
        photo_name = photo.filename
        photo_data = photo.download().raw
        with open(f'downloaded_photos/{photo_name}', 'wb') as file:
            file.write(photo_data)
        print(f'Downloaded {photo_name}')

    print("Downloaded recent 10 photos.")

setupLogging()
authenticate()
fetch_photos()