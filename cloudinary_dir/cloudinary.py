import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from dotenv import load_dotenv
import os

# Use the python-dotenv library to load the environment variables from the .env file into the process's environment variables.
load_dotenv()

# Use cloudinary.config() to set up the authentication information required for accessing the Cloudinary API.
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)