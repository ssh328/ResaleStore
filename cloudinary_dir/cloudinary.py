# Cloudinary와 관련된 필수 모듈 임포트
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# 환경 변수 로드하기 위한 모듈 임포트
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# Cloudinary 설정
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)