# ResaleStore

## 프로젝트 소개
<<<<<<< HEAD
이 프로젝트는 "중고 거래 사이트"를 주제로 한 Flask 웹 애플리케이션입니다. 사용자 관리, 게시물 작성, 채팅 기능, 리뷰 작성 등을 제공합니다.

## 실행 방법

### 1. 프로젝트 다운로드
두 가지 방법 중 선택하여 진행:

### 5. 환경 변수 설정
=======
이 프로젝트는 "중고 거래 사이트"를 주제로 한 Flask 웹 애플리케이션입니다. 사용자들이 중고 물품을 쉽게 거래할 수 있도록 다양한 기능을 제공합니다.

## 📌주요 기능
### 사용자 관리
- 회원가입 및 로그인
- 프로필 수정
- 비밀번호 수정
- 회원 탈퇴 기능
- 본인 게시물 관리
- 좋아요 상품 관리

### 게시물 관리
- 판매 게시물 작성/수정/삭제
- 이미지 업로드 기능
- 카테고리별 분류
- 검색 및 필터링
- 좋아요 시스템

### 채팅 기능
- 실시간 1:1 채팅
- 채팅방 목록 관리
- 이전 대화 내역 조회

### 리뷰 시스템
- 거래 후기 작성
- 별점 평가

## ⚙️기술 스택
### Frontend
- HTML5
- CSS
- JavaScript
- Bootstrap 5

### Backend
- Python
- Flask
- SQLAlchemy (ORM)
- Flask-SocketIO (실시간 채팅)
- Cloudinary
- Flask-WTF
- Flask-Login
- Werkzeug Security

### Database
- SQLite3

## 💻실행 방법
1. Git clone 사용 또는, 다운로드
```
cd ResaleStore
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. .env 파일 생성 후 아래 내용 추가
- CLOUDINARY_CLOUD_NAME=your-cloud-name
- CLOUDINARY_API_KEY=your-api-key
- CLOUDINARY_API_SECRET=your-api-secret
- SECRET_KEY=your-secret-key
- SQLALCHEMY_DATABASE_URI=your-database-uri
- ADMIN_USER_ID=your-admin-id
3. 앱 실행
```
python main.py
```
4. 웹 브라우저 접속 <http://127.0.0.1:5000/>
>>>>>>> dbb86ea4df33be8541acdc511dc49f58c103e6ce
