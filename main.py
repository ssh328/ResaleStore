from flask import render_template, jsonify
from flask_login import current_user
from dotenv import load_dotenv
import os

from security.security import login_manager
from routes.chat import socketio
from app import app
from model.data import db, User, Post, Like
from routes.users import users
from routes.posts import posts
from routes.chat import chatting

# Use the python-dotenv library to load the environment variables from the .env file into the process's environment variables.
load_dotenv()


# Set the secret key from the environment variable
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Flask_Login
login_manager.init_app(app)


# Set the database URI from the environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
# Disable the SQLAlchemy modification tracking
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy
db.init_app(app)


# Create the database
with app.app_context():
    db.create_all()


# Login management
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

# Main page
@app.route('/')
def home():
    return render_template('home.html', logged_in=current_user.is_authenticated)


# Register the blueprints
app.register_blueprint(users, url_prefix='/')
app.register_blueprint(posts, url_prefix='/posts')
app.register_blueprint(chatting, url_prefix='/chat')


@app.route('/increase/<string:post_id>', methods=["POST"])
def increase(post_id):
    """
    Toggle the like status of the given post_id
    If the user has already liked the post, remove the like, otherwise add a like
    The like count of the post is updated and returned in JSON format
    """
    post = db.get_or_404(Post, post_id)

    like = Like.query.filter_by(user_email=current_user.email, post_id=post_id).first()

    if like:
        db.session.delete(like)
        post.like_cnt -= 1

    else:
        new_like = Like(user_email=current_user.email, post_id=post_id)
        db.session.add(new_like)
        post.like_cnt += 1

    db.session.commit()

    return jsonify({
        'like_cnt': post.like_cnt
        })


if __name__ == '__main__' :
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)