from flask import render_template, url_for, request, redirect, flash, Blueprint, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
from sqlalchemy import or_
from forms import SignUpForm, LoginForm, ChangePasswordForm
from model.data import db, User, Post, Like, Room, Review
from security.security import admin_only
from cloudinary_dir.cloudinary import cloudinary
import cloudinary.uploader

# Blueprint for the users routes
users = Blueprint('users', __name__, template_folder='templates/users')

# Define the allowed file extensions.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension
    
    Parameters:
        filename (str): The name of the file to check
    
    Returns:
        bool: True if the extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@users.route('/login', methods=['GET', 'POST'])
def login():
    """
    Function that provides login functionality

    - Users can log in by entering their email and password
    - Redirects to the main page upon successful login

    Returns:
        template: Login page
    """
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            flash('반갑습니다!', 'success')
            return redirect(url_for('posts.all_products'))
        else:
            flash('회원정보가 일치하지 않아요!', 'danger')
            return redirect(url_for('users.login'))

    return render_template('users/login.html', form=form)


@users.route('/logout')
def logout():
    """
    Function that provides logout functionality

    - Logs out the currently logged in user

    Returns:
        redirect: The post list page
    """
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('posts.all_products'))


@users.route('/register', methods=['GET', 'POST'])
def register():
    """
    Function that provides registration functionality

    - Users can register by entering their email, password, etc.
    - Redirects to the main page after successful registration

    Returns:
        template: The registration page
    """
    form = SignUpForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=request.form.get('email')).first():
            flash('이미 가입된 이메일이 있어요!', 'danger')
            return redirect(url_for('users.login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            name=request.form.get('name'),
            email=request.form.get('email'),
            password=hash_and_salted_password,
            profile_image_name = 'https://res.cloudinary.com/dccnoyixy/image/upload/v1737569274/Products/xunetnnx7ajjqo2vay3z.png',
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name')
        )

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('회원가입이 완료되었습니다!', 'success')
        return redirect(url_for('posts.all_products'))
    return render_template('users/register.html', form=form)


@users.route('/my_page')
@admin_only
def my_page():
    """
    Function that displays the my page

    - Displays the current user's posts and liked posts

    Returns:
        template: The my page
    """
    author_post = Post.query.filter_by(author_id=current_user.id).all()

    like_post = Like.query.filter_by(user_email=current_user.email).all()
    like_post_list = [Post.query.get(like.post_id) for like in like_post]

    like_posts = []
    if current_user.is_authenticated:
        like_posts = [like.post_id for like in current_user.likes]

    if current_user.profile_image_name:
        img_path = url_for('static', filename=f'uploads/{current_user.profile_image_name}')
        return render_template('users/my_page.html', name=current_user.name,
                               logged_in=current_user.is_authenticated,
                               all_data=author_post,
                               all_like_post_data=like_post_list,
                               like_posts=like_posts,
                               img_path=img_path
                               )

    return render_template('users/my_page.html', name=current_user.name,
                           logged_in=current_user.is_authenticated,
                           all_data=author_post,
                           all_like_post_data=like_post_list,
                           like_posts=like_posts,
                           )


@users.route('/upload/<string:user_id>', methods=['GET', 'POST'])
@admin_only
def upload_profile_image(user_id):
    """
    Function that uploads a profile image

    - Users can upload a new profile image
    - Deletes the previous image and updates with the new image

    Parameters:
        user_id (str): The ID of the user to upload the profile image to

    Returns:
        redirect: The my page
    """
    if request.method == "POST":

        requested_user_id = db.get_or_404(User, user_id)

        if 'img' not in request.files:
            flash("파일이 없습니다.")
            return redirect(url_for('users.my_page', name=current_user.name,
                                    logged_in=current_user.is_authenticated))

        file = request.files['img']

        if file.filename == '':
            flash("선택된 파일이 없습니다.")
            return redirect(url_for('users.my_page', name=current_user.name,
                                    logged_in=current_user.is_authenticated))
        
        if not allowed_file(file.filename):
            invalid_file = file.filename
            flash(f"허용되지 않은 파일 형식: {invalid_file}", 'danger')
            return redirect(url_for('users.my_page', name=current_user.name,
                                    logged_in=current_user.is_authenticated))

        previous_image_url = requested_user_id.profile_image_name

        response = cloudinary.uploader.upload(file, folder="Products")
        img_url = response['secure_url']

        if previous_image_url:
            if previous_image_url != 'https://res.cloudinary.com/dccnoyixy/image/upload/v1737569274/Products/xunetnnx7ajjqo2vay3z.png':
                public_id = previous_image_url.split('/')[-1].split('.')[0]  # URL에서 public_id 추출
                cloudinary.uploader.destroy(f"Products/{public_id}")  # Cloudinary에서 이미지 삭제

        requested_user_id.profile_image_name = img_url
        db.session.commit()

        flash('프로필 이미지가 업데이트 되었습니다.', 'success')
        return redirect(url_for('users.profile_edit', 
                                name=current_user.name, 
                                logged_in=current_user.is_authenticated, 
                                current_user=current_user))
    
    return render_template('users/my_page.html', name=current_user.name, logged_in=current_user.is_authenticated)


@users.route('/my_page/profile_edit')
@admin_only
def profile_edit():
    """
    Function that displays the profile edit page

    Returns:
        template: The profile edit page
    """
    return render_template('users/profile_edit.html', 
                           name=current_user.name, 
                           logged_in=current_user.is_authenticated,
                           current_user=current_user)


@users.route('/my_page/my_post')
@admin_only
def my_post():
    """
    Function that displays the user's posts

    - Displays the user's posts using pagination

    Returns:
        template: The user's posts page
    """
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author_id=current_user.id).paginate(page=page, per_page=20, error_out=False)

    like_posts = []
    if current_user.is_authenticated:
        like_posts = [like.post_id for like in current_user.likes]

    return render_template('users/my_post.html', 
                           logged_in=current_user.is_authenticated, 
                           all_data=posts.items,
                           pagination=posts,
                           like_posts=like_posts)


@users.route('/my_page/like_post')
@admin_only
def like_post():
    """
    Function that displays the user's liked posts

    - Displays the user's liked posts using pagination

    Returns:
        template: The user's liked posts page
    """
    page = request.args.get('page', 1, type=int)
    posts = Like.query.filter_by(user_email=current_user.email).paginate(page=page, per_page=20, error_out=False)
    like_post_list = [Post.query.get(like.post_id) for like in posts.items]

    like_posts = []
    if current_user.is_authenticated:
        like_posts = [like.post_id for like in current_user.likes]

    return render_template('users/like_post.html',
                            logged_in=current_user.is_authenticated,
                            all_like_post_data=like_post_list,
                            pagination=posts,
                            like_posts=like_posts)


@users.route('/change_password', methods=['GET', 'POST'])
@admin_only
def change_password():
    """
    Function that provides password change functionality

    - Users can change their password by entering their current password

    Returns:
        template: The password change page
    """
    form = LoginForm()
    change_password_form = ChangePasswordForm()
    authenticated = None

    if change_password_form.validate_on_submit():
        new_password = change_password_form.new_password.data
        hash_and_salted_password = generate_password_hash(
            new_password,
            method='pbkdf2:sha256',
            salt_length=8
        )
        current_user.password = hash_and_salted_password
        db.session.commit()
        flash('비밀번호가 변경되었습니다.', 'success')
        return redirect(url_for('users.profile_edit'))

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if current_user.email == email and check_password_hash(current_user.password, password):
            return redirect(url_for('users.change_password', is_authenticated=True))
        else:
            flash('다시 시도하세요.', 'danger')
            return redirect(url_for('users.change_password'))
    
    if request.args.get('is_authenticated'):
        authenticated = True

    return render_template('users/change_password.html', form=form, change_password_form=change_password_form, logged_in=current_user.is_authenticated, authenticated=authenticated)


@users.route('/delete_account', methods=['GET', 'POST'])
@admin_only
def delete_account():
    """
    Function that provides account deletion functionality

    - Users can delete their account after verifying their identity
    - When an account is deleted, the user's posts and chat room information are updated
    - When the account deletion is complete, the user is redirected to the main page

    Returns:
        redirect: The home page
    """
    form = LoginForm()
    authenticated = None

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if current_user.email == email and check_password_hash(current_user.password, password):
            return redirect(url_for('users.delete_account', is_authenticated=True))
        else:
            flash('다시 시도하세요.', 'danger')
            return redirect(url_for('users.delete_account'))

    if request.method == 'POST':
        current_account = db.get_or_404(User, current_user.id)

        posts = Post.query.filter_by(author_id = current_user.id).all()
        for post in posts:
            db.session.delete(post)

        rooms = Room.query.filter(or_(Room.sender_id == current_user.id, Room.receiver_id == current_user.id)).all()
        for room in rooms:
            if room.sender_id == current_user.id:
                room.sender_id = "Unknown"
                room.sender_join = False
            else:
                room.receiver_id = "Unknown"
                room.receiver_join = False

        db.session.commit()

        db.session.delete(current_account)
        db.session.commit()

        flash('계정이 삭제되었습니다.', 'success')
        return redirect(url_for('home'))

    if request.args.get('is_authenticated'):
        authenticated = True

    return render_template('users/delete_account.html', form=form, logged_in=current_user.is_authenticated, authenticated=authenticated)


@users.route('/users/<string:user_name>')
@admin_only
def user_profile(user_name):
    """
    Function that displays the user's profile page

    - Searches for a user by the given user name
    - Loads all posts written by the user using pagination
    - Loads all reviews received by the user and the profile image of the review writer
    - Loads the list of post IDs liked by the currently logged in user

    Parameters:
        user_name (str): The name of the user to display the profile for

    Returns:
        template: The user's profile page
    """
    user = User.query.filter_by(name=user_name).first_or_404()
    page = request.args.get('page', 1, type=int)

    posts = Post.query.filter_by(author_id=user.id).order_by(Post.date.desc()).paginate(page=page, per_page=20, error_out=False)
    
    reviews_query = db.session.query(Review, User.profile_image_name)\
        .join(User, Review.review_writer == User.name)\
        .filter(Review.user_name == user.name)\
        .all()
        
    reviews = [{
        'review': review.review,
        'profile_image': profile_image,
        'rating': review.rating,
        'review_writer': review.review_writer,
        'review_id': review.id
    } for review, profile_image in reviews_query]

    like_posts = []
    if current_user.is_authenticated:
        like_posts = [like.post_id for like in current_user.likes]

    return render_template('users/user_profile.html',
                           user=user,
                           logged_in=current_user.is_authenticated, 
                           all_data=posts.items,
                           pagination=posts,
                           like_posts=like_posts,
                           reviews=reviews
                           )


# 리뷰 등록
@users.route('/reviews', methods=['POST'])
@admin_only
def reviews():
    """
    Function that handles review submission

    - Allows users to submit reviews through POST requests
    - Retrieves review text, user name, and rating from form data
    - If no rating is provided, uses a default value of 1
    - Creates a new review object and adds it to the database
    - If successful, redirects to the user's profile page
    - If submission fails, flashes an error message and redirects to the user's profile page

    Returns:
        redirect: The user's profile page
    """
    if request.method == 'POST':
        review_text = request.form.get('review')
        user_name = request.args.get('user_name')
        rating = request.form.get('rating')

        if rating == None:
            rating = 1

        new_review = Review(
            user_name=user_name,
            review=review_text,
            review_writer=current_user.name,
            rating=rating
        )
        
        db.session.add(new_review)
        db.session.commit()

        flash('리뷰가 등록되었습니다.', 'success')
        return redirect(url_for('users.user_profile', user_name=user_name))
    else:
        flash('리뷰 등록에 실패했습니다. 다시 시도해주세요.', 'danger')
        return redirect(url_for('users.user_profile', user_name=request.args.get('user_name')))
    

# 리뷰 삭제
@users.route('/delete_review', methods=['POST'])
@admin_only
def delete_review():
    """
    Function that handles review deletion

    - Deletes a review based on the provided review ID
    - Redirects to the user's profile page after deletion

    Returns:
        redirect: The user's profile page
    """
    review_id = request.args.get('review_id')
    review = Review.query.get(review_id)
    db.session.delete(review)
    db.session.commit()

    flash('리뷰가 삭제되었습니다.', 'success')
    return redirect(url_for('users.user_profile', user_name=review.user_name))