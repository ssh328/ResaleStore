import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from dotenv import load_dotenv
import os

# python-dotenv 라이브러리를 사용하여 .env 파일의 환경 변수들을 프로세스의 환경 변수로 로드
load_dotenv()

# cloudinary.config()를 사용하여 Cloudinary API 접근에 필요한 인증 정보를 설정
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)