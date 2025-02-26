from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import DeclarativeBase
import uuid


class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy models
    
    This defines a base class that serves as the foundation for all model classes,
    inheriting from DeclarativeBase used in SQLAlchemy version 3.0+.
    """
    pass


# Create SQLAlchemy database instance
db = SQLAlchemy(model_class=Base)


class User(UserMixin, db.Model):
    """
    A model that stores user information
    
    Attributes:
        id (str): Unique identifier for the user (UUID)
        first_name (str): User's first name
        last_name (str): User's last name
        name (str): User's nickname
        email (str): User's email
        password (str): Encrypted password
        profile_image_name (str): Profile image file name
        
    Relationships:
        likes: Relationship with posts that the user liked
        author_posts: Relationship with posts authored by the user
        room_sender: Relationship with chat rooms sent by the user
        room_receiver: Relationship with chat rooms received by the user
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
    A model that stores post information
    
    Attributes:
        id (str): Unique identifier for the post
        title (str): Title of the post
        date (DateTime): Date the post was created
        body (Text): Content of the post
        price (int): Price of the item
        img_url (str): Image URL
        like_cnt (int): Number of likes
        category (str): Category of the post
        author_id (str): ID of the post's author (foreign key)
        
    Relationships:
        liked_by: Relationship with users who liked the post (1:N relationship with Like model)
        author: Relationship with the author of the post (N:1 relationship with User model)
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
    Model used when a user likes a post
    
    Attributes:
        id (str): Unique identifier for the like
        user_email (str): Email of the user who liked the post (foreign key)
        post_id (str): ID of the post that was liked (foreign key)
        
    Relationships:
        user: Relationship with the user who liked the post
        post: Relationship with the post that was liked
    """
    __tablename__= "likes"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    user_email = db.Column(db.String(100), db.ForeignKey('users.email'))
    post_id = db.Column(db.String(36), db.ForeignKey('posts.id'))

    user = db.relationship('User', back_populates='likes')
    post = db.relationship('Post', back_populates='liked_by')


class Room(db.Model):
    """
    A model that manages chat rooms between users
    
    Attributes:
        id (str): Unique identifier for the chat room
        sender_id (str): ID of the user who created the chat room
        receiver_id (str): ID of the chat counterpart
        date (DateTime): Date and time when the chat room was created
        sender_last_join (DateTime): Last time the sender joined
        receiver_last_join (DateTime): Last time the receiver joined
        sender_unread_count (int): Number of unread messages for the sender
        receiver_unread_count (int): Number of unread messages for the receiver
        sender_join (bool): Participation status of the sender in the chat room
        receiver_join (bool): Participation status of the receiver in the chat room
        sender_stay_join (bool): Real-time connection status of the sender
        receiver_stay_join (bool): Real-time connection status of the receiver
        
    Relationships:
        sender: Relationship with the creator of the chat room
        receiver: Relationship with the chat counterpart
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
    A model that stores messages in the chat room
    
    Attributes:
        id (str): Unique identifier for the message
        sender_name (str): Name of the message sender (foreign key)
        receive_user_name (str): Name of the message receiver
        room_id (str): ID of the chat room to which the message belongs (foreign key)
        text (Text): Content of the message
        time (DateTime): Time when the message was sent
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
    A model that stores reviews written after transactions between users
    
    Attributes:
        id (str): Unique identifier for the review
        user_name (str): Name of the user being reviewed
        review_writer (str): Name of the reviewer (foreign key)
        review (Text): Content of the review (foreign key)
        rating (int): Rating
    """
    __tablename__ = "reviews"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_name = db.Column(db.String(100), db.ForeignKey('users.name'), nullable=False)
    review_writer = db.Column(db.String(100), db.ForeignKey('users.name'), nullable=False)
    review = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)