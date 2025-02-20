from flask import render_template, url_for, request, redirect, flash, Blueprint, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
from sqlalchemy import or_
from forms import SignUpForm, LoginForm, ChangePasswordForm
from model.data import db, User, Post, Like, Room, Review
from security.security import admin_only
from cloudinary_dir.cloudinary import cloudinary
import cloudinary.uploader

users = Blueprint('users', __name__, template_folder='templates/users')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 로그인 창
@users.route('/login', methods=['GET', 'POST'])
def login():
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


# 로그아웃 창
@users.route('/logout')
def logout():
    logout_user()
    flash('로그아웃 되었습니다!', 'success')
    return redirect(url_for('posts.all_products'))


# 회원가입 창
@users.route('/register', methods=['GET', 'POST'])
def register():
    form = SignUpForm()
    if form.validate_on_submit():   # 사용자가 폼을 post 한 후 유효성 검증이 성공한 경우 True

        if User.query.filter_by(email=request.form.get('email')).first():
            flash('이미 가입된 이메일이 있어요!', 'danger')
            return redirect(url_for('users.login'))

        # PASSWORD HASHING
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
        login_user(new_user)  # 데이터베이스에 세부 사항을 추가한 후 로그인하고 사용자를 인증
        flash('회원가입이 완료되었습니다!', 'success')
        return redirect(url_for('posts.all_products'))
    return render_template('users/register.html', form=form)


# 마이 페이지 창
@users.route('/my_page')
@admin_only
def my_page():
    # 현재 유저가 작성한 모든 게시물 불러옴
    author_post = Post.query.filter_by(author_id=current_user.id).all()

    # 현재 유저가 좋아요 버튼을 누른 모든 게시물을 불러옴
    # Like 데이터베이스에서 로그인 된 email 과 일치된 데이터를 불러옴
    like_post = Like.query.filter_by(user_email=current_user.email).all()
    like_post_list = [Post.query.get(like.post_id) for like in like_post]

    # 현재 로그인 한 유저가 좋아요 누른 게시물 id 목록을 가져옴
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


# 프로필 이미지 업로드
@users.route('/upload/<string:user_id>', methods=['GET', 'POST'])
@admin_only
def upload_profile_image(user_id):
    if request.method == "POST":

        requested_user_id = db.get_or_404(User, user_id)

        # 파일이 첨부되었는지 확인
        if 'img' not in request.files:
            flash("파일이 없습니다.")
            return redirect(url_for('users.my_page', name=current_user.name,
                                    logged_in=current_user.is_authenticated))

        file = request.files['img']

        # 파일 이름이 비어있는 경우
        if file.filename == '':
            flash("선택된 파일이 없습니다.")
            return redirect(url_for('users.my_page', name=current_user.name,
                                    logged_in=current_user.is_authenticated))
        
        if not allowed_file(file.filename):
            invalid_file = file.filename
            flash(f"허용되지 않은 파일 형식: {invalid_file}", 'danger')
            return redirect(url_for('users.my_page', name=current_user.name,
                                    logged_in=current_user.is_authenticated))

        # 이전 프로필 이미지 URL 저장
        previous_image_url = requested_user_id.profile_image_name

        response = cloudinary.uploader.upload(file, folder="Products")
        img_url = response['secure_url']

        # 이전 이미지 삭제
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


# 프로필 수정 창
@users.route('/my_page/profile_edit')
@admin_only
def profile_edit():
    return render_template('users/profile_edit.html', 
                           name=current_user.name, 
                           logged_in=current_user.is_authenticated,
                           current_user=current_user)


# 내가 작성한 게시물 창
@users.route('/my_page/my_post')
@admin_only
def my_post():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author_id=current_user.id).paginate(page=page, per_page=20, error_out=False)

    # 현재 로그인 한 유저가 좋아요 누른 게시물 id 목록을 가져옴
    like_posts = []
    if current_user.is_authenticated:
        like_posts = [like.post_id for like in current_user.likes]

    return render_template('users/my_post.html', 
                           logged_in=current_user.is_authenticated, 
                           all_data=posts.items,
                           pagination=posts,
                           like_posts=like_posts)


# 내가 좋아요 누른 게시물 창
@users.route('/my_page/like_post')
@admin_only
def like_post():
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


# 비밀번호 변경
@users.route('/change_password', methods=['GET', 'POST'])
@admin_only
def change_password():
    form = LoginForm()
    change_password_form = ChangePasswordForm()
    authenticated = None

    # 비밀번호 변경 폼 제출
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

    # 본인 인증
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if current_user.email == email and check_password_hash(current_user.password, password):
            return redirect(url_for('users.change_password', is_authenticated=True))
        else:
            flash('다시 시도하세요.', 'danger')
            return redirect(url_for('users.change_password'))
    
    # 본인 인증 여부
    if request.args.get('is_authenticated'):
        authenticated = True

    return render_template('users/change_password.html', form=form, change_password_form=change_password_form, logged_in=current_user.is_authenticated, authenticated=authenticated)


# 계정 삭제
@users.route('/delete_account', methods=['GET', 'POST'])
@admin_only
def delete_account():
    form = LoginForm()
    authenticated = None

    # 본인 인증
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if current_user.email == email and check_password_hash(current_user.password, password):
            return redirect(url_for('users.delete_account', is_authenticated=True))
        else:
            flash('다시 시도하세요.', 'danger')
            return redirect(url_for('users.delete_account'))

    # 계정 삭제
    if request.method == 'POST':
        current_account = db.get_or_404(User, current_user.id)

        posts = Post.query.filter_by(author_id = current_user.id).all()
        for post in posts:
            db.session.delete(post)

        # 현재 사용자가 참여하고 있는 모든 채팅방 삭제
        rooms = Room.query.filter(or_(Room.sender_id == current_user.id, Room.receiver_id == current_user.id)).all()
        for room in rooms:
            if room.sender_id == current_user.id:
                room.sender_id = "Unknown"  # 기본 사용자 ID로 변경
                room.sender_join = False
            else:
                room.receiver_id = "Unknown"  # 기본 사용자 ID로 변경
                room.receiver_join = False

        # 변경된 채팅방을 커밋
        db.session.commit()  # 여기서 커밋을 추가하여 변경 사항을 저장합니다.

        db.session.delete(current_account)
        db.session.commit()

        flash('계정이 삭제되었습니다.', 'success')
        return redirect(url_for('index'))

    # 본인 인증 여부
    if request.args.get('is_authenticated'):
        authenticated = True

    return render_template('users/delete_account.html', form=form, logged_in=current_user.is_authenticated, authenticated=authenticated)


# 유저 프로필 창
@users.route('/users/<string:user_name>')
def user_profile(user_name):
    # get_or_404(): 기본적으로 기본키를 사용
    # 이를 해결하기 위해 filter_by() 사용
    user = User.query.filter_by(name=user_name).first_or_404()  # user_name 대신 name 필드로 검색
    page = request.args.get('page', 1, type=int)

    # 상대 유저가 작성한 모든 게시물 불러옴
    posts = Post.query.filter_by(author_id=user.id).order_by(Post.date.desc()).paginate(page=page, per_page=20, error_out=False)
    
    reviews_query = db.session.query(Review, User.profile_image_name)\
        .join(User, Review.review_writer == User.name)\
        .filter(Review.user_name == user.name)\
        .all()
        
    # 쿼리 결과를 사용하기 쉬운 형태로 변환
    reviews = [{
        'review': review.review,
        'profile_image': profile_image,
        'rating': review.rating,
        'review_writer': review.review_writer,
        'review_id': review.id
    } for review, profile_image in reviews_query]

    # 현재 로그인 한 유저가 좋아요 누른 게시물 id 목록을 가져옴
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
    review_id = request.args.get('review_id')
    review = Review.query.get(review_id)
    db.session.delete(review)
    db.session.commit()

    flash('리뷰가 삭제되었습니다.', 'success')
    return redirect(url_for('users.user_profile', user_name=review.user_name))