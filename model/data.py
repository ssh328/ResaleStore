from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import DeclarativeBase
import uuid


class Base(DeclarativeBase):
    """
    SQLAlchemy 모델을 위한 기본 클래스
    
    이 클래스는 모든 모델 클래스의 기초가 되며, SQLAlchemy 버전 3.0 이상에서 사용되는
    DeclarativeBase를 상속
    """
    pass


# Create SQLAlchemy database instance
db = SQLAlchemy(model_class=Base)


class User(UserMixin, db.Model):
    """
    사용자 정보를 저장하는 모델
    
    Attributes:
        id (str): 사용자의 고유 식별자 (UUID)
        first_name (str): 사용자의 이름
        last_name (str): 사용자의 성
        name (str): 사용자의 닉네임
        email (str): 사용자의 이메일
        password (str): 암호화된 비밀번호
        profile_image_name (str): 프로필 이미지 파일명
        
    Relationships:
        likes: 사용자가 좋아요한 게시물과의 관계
        author_posts: 사용자가 작성한 게시물과의 관계
        room_sender: 사용자가 보낸 채팅방과의 관계
        room_receiver: 사용자가 받은 채팅방과의 관계
    """
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    profile_image_name = db.Column(db.String(255))

    likes = db.relationship('Like', back_populates='user')
    author_posts = db.relationship("Post", back_populates="author")
    room_sender = db.relationship("Room", foreign_keys="Room.sender_id", back_populates="sender")
    room_receiver = db.relationship("Room", foreign_keys="Room.receiver_id", back_populates="receiver")


class Post(db.Model):
    """
    게시물 정보를 저장하는 모델
    
    Attributes:
        id (str): 게시물의 고유 식별자
        title (str): 게시물 제목
        date (DateTime): 게시물 작성일
        body (Text): 게시물 내용
        price (int): 상품 가격
        img_url (str): 이미지 URL
        like_cnt (int): 좋아요 수
        category (str): 게시물 카테고리
        author_id (str): 작성자 ID (외래 키)
        
    Relationships:
        liked_by: 게시물을 좋아요한 사용자와의 관계 (Like 모델과 1:N 관계)
        author: 게시물 작성자와의 관계 (User 모델과 N:1 관계)
    """
    __tablename__ = "posts"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(250), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    body = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    like_cnt = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(250), nullable=False)

    author_id = db.Column(db.String(36), db.ForeignKey("users.id"))

    liked_by = db.relationship('Like', back_populates='post')
    author = db.relationship("User", back_populates="author_posts")


class Like(db.Model):
    """
    사용자가 게시물에 좋아요를 눌렀을 때 사용되는 모델
    
    Attributes:
        id (str): 좋아요의 고유 식별자
        user_email (str): 좋아요를 누른 사용자의 이메일 (외래 키)
        post_id (str): 좋아요가 눌린 게시물의 ID (외래 키)
        
    Relationships:
        user: 좋아요를 누른 사용자와의 관계
        post: 좋아요가 눌린 게시물과의 관계
    """
    __tablename__= "likes"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    user_email = db.Column(db.String(100), db.ForeignKey('users.email'))
    post_id = db.Column(db.String(36), db.ForeignKey('posts.id'))

    user = db.relationship('User', back_populates='likes')
    post = db.relationship('Post', back_populates='liked_by')


class Room(db.Model):
    """
    사용자 간의 채팅방을 관리하는 모델
    
    Attributes:
        id (str): 채팅방의 고유 식별자
        sender_id (str): 채팅방을 생성한 사용자의 ID
        receiver_id (str): 채팅 상대방의 ID
        date (DateTime): 채팅방 생성 일시
        sender_last_join (DateTime): 발신자의 마지막 참여 시간
        receiver_last_join (DateTime): 수신자의 마지막 참여 시간
        sender_unread_count (int): 발신자의 읽지 않은 메시지 수
        receiver_unread_count (int): 수신자의 읽지 않은 메시지 수
        sender_join (bool): 발신자의 채팅방 참여 상태
        receiver_join (bool): 수신자의 채팅방 참여 상태
        sender_stay_join (bool): 발신자의 실시간 연결 상태
        receiver_stay_join (bool): 수신자의 실시간 연결 상태
        
    Relationships:
        sender: 채팅방 생성자와의 관계
        receiver: 채팅 상대방과의 관계
    """
    __tablename__ = "rooms"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    sender_last_join = db.Column(db.DateTime, nullable=True)
    receiver_last_join = db.Column(db.DateTime, nullable=True)
    sender_unread_count = db.Column(db.Integer, default=0)
    receiver_unread_count = db.Column(db.Integer, default=0)

    sender_join = db.Column(db.Boolean, nullable=False, default=False)
    receiver_join = db.Column(db.Boolean, nullable=False, default=False)

    sender_stay_join = db.Column(db.Boolean, nullable=False, default=False)
    receiver_stay_join = db.Column(db.Boolean, nullable=False, default=False)

    sender = db.relationship("User", foreign_keys=[sender_id], back_populates="room_sender")
    receiver = db.relationship("User", foreign_keys=[receiver_id], back_populates="room_receiver")


class Message(db.Model):
    """
    채팅방의 메시지를 저장하는 모델
    
    Attributes:
        id (str): 메시지의 고유 식별자
        sender_name (str): 메시지 발신자의 이름 (외래 키)
        receive_user_name (str): 메시지 수신자의 이름
        room_id (str): 메시지가 속한 채팅방의 ID (외래 키)
        text (Text): 메시지 내용
        time (DateTime): 메시지 전송 시간
    """
    __tablename__ = "messages"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_name = db.Column(db.String(100), db.ForeignKey('users.name'), nullable=False)
    receive_user_name = db.Column(db.String(36), nullable=False)
    room_id = db.Column(db.String(36), db.ForeignKey('rooms.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False)


class Review(db.Model):
    """
    사용자 간 거래 후 작성되는 리뷰를 저장하는 모델
    
    Attributes:
        id (str): 리뷰의 고유 식별자
        user_name (str): 리뷰 대상 사용자의 이름
        review_writer (str): 리뷰 작성자의 이름 (외래 키)
        review (Text): 리뷰 내용 (외래 키)
        rating (int): 평점
    """
    __tablename__ = "reviews"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_name = db.Column(db.String(100), db.ForeignKey('users.name'), nullable=False)
    review_writer = db.Column(db.String(100), db.ForeignKey('users.name'), nullable=False)
    review = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)