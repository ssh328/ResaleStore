from dotenv import load_dotenv
import os
from flask import render_template, url_for, request, redirect, flash, jsonify, Blueprint
from datetime import datetime
from flask_login import current_user
from model.data import Post, db, Like
from forms import CreatePostForm
from security.security import admin_only, is_author
from cloudinary_dir.cloudinary import cloudinary
import cloudinary.uploader

# .env 파일에서 환경 변수를 프로세스의 환경 변수로 로드하기 위해 python-dotenv 라이브러리를 사용
load_dotenv()
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# posts 라우트를 위한 Blueprint
posts = Blueprint('posts', __name__, template_folder='templates/product')

def allowed_file(filename):
    """
    업로드된 파일이 허용된 확장자를 가지고 있는지 확인
    
    Parameters:
        filename (str): 확인할 파일 이름
    
    Returns:
        bool: 확장자가 허용되면 True, 그렇지 않으면 False
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def search_posts(query):
    """
    게시물 제목에서 검색어를 포함하는 게시물을 검색
    
    Parameters:
        query (str): 검색할 키워드
    
    Returns:
        Select: 검색 결과를 포함하는 쿼리 객체
    """
    return db.select(Post).filter(Post.title.contains(query)).order_by(Post.date.desc())


# 모든 게시물 보여주는 창
@posts.route('/all-products', methods=['GET', "POST"])
def all_products():
    """
    모든 게시물을 표시하는 함수

    - 카테고리별 필터링
    - 정렬 기능 (최신순, 인기순)
    - 가격대별 필터링
    - 검색 기능
    - 페이지네이션 구현

    Returns:
        template: 게시물 목록 페이지
    """
    categories = [
        "디지털기기", "생활가전", "가구/인테리어", "생활/주방", "유아동", "유아도서",
        "여성의류", "여성잡화", "남성패션/잡화", "뷰티/미용", "스포츠/레저", "취미/게임/음반",
        "도서", "티켓/교환권", "가공식품", "건강기능식품", "반려동물용품", "식물", "기타 중고물품"
    ]

    like_posts = []
    if current_user.is_authenticated:
        like_posts = [like.post_id for like in current_user.likes]

    page = request.args.get('page', 1, type=int)

    category = request.args.get('category', default=None)
    sort_by = request.args.get('sort_by', default='recent')
    start_price = request.args.get('start_price', type=int)
    end_price = request.args.get('end_price', type=int)

    query = db.select(Post)

    if category:
        query = query.filter(Post.category == category)

    if sort_by:
        if sort_by == "recent":
            query = query.order_by(Post.date.desc())
        elif sort_by == "hottest":
            query = query.order_by(Post.like_cnt.desc(), Post.date.desc())

    if start_price is not None and end_price is not None:
        query = query.filter(Post.price.between(start_price, end_price))

    search_query = request.args.get('search', default=None)
    if search_query:
        query = search_posts(search_query)

    posts = db.paginate(query, page=page, per_page=20, error_out=False)

    return render_template(
        'product/all-products.html',
        all_data=posts.items,
        logged_in=current_user.is_authenticated,
        pagination=posts,
        like_posts=like_posts,
        categories=categories,
        category=category,
        sort_by=sort_by,
        startPrice=start_price,
        endPrice=end_price
    )


@posts.route('/post/<string:post_id>', methods=["GET", "POST"])
def show_post(post_id):
    """
    특정 게시물의 상세 내용을 표시하는 함수

    Parameters:
        post_id (str): 조회할 게시물의 ID

    Returns:
        template: 게시물 상세 페이지
    """
    requested_post = db.get_or_404(Post, post_id)

    img_urls = requested_post.img_url.split(',') if requested_post.img_url else []

    return render_template('product/post.html', requested_post=requested_post,
                           logged_in=current_user.is_authenticated, img_urls=img_urls,
                           ADMIN_USER_ID=ADMIN_USER_ID)


@posts.route('/new-products-post', methods=['GET', 'POST'])
@admin_only
def add_new_products_post():
    """
    새 게시물을 생성하는 함수

    - 관리자만 접근 가능
    - 다중 이미지 업로드 지원
    - Cloudinary를 사용하여 이미지 저장

    Returns:
        template: 게시물 생성 페이지 또는 생성된 게시물로 리다이렉트
    """
    form = CreatePostForm()
    if request.method == "POST":
        title = form.title.data
        price = form.price.data
        category = form.category.data
        textarea = form.textarea.data
        files = request.files.getlist('files')

        invalid_files = [file.filename for file in files if not allowed_file(file.filename)]

        if invalid_files:
            flash(f"허용되지 않은 파일 형식: {', '.join(invalid_files)}", 'danger')
            return redirect(url_for('posts.add_new_products_post'))

        img_url_list = []
        public_id_list = []

        for file in files:
            response = cloudinary.uploader.upload(file, folder="Products")
            img_url = response['secure_url']
            public_id = response['public_id']
            img_url_list.append(img_url)
            public_id_list.append(public_id)

        img_urls_str = ','.join(img_url_list)

        new_post = Post(title=title,
                        date=datetime.now(),
                        body=textarea,
                        price=price,
                        category=category,
                        img_url=img_urls_str,
                        author=current_user)

        db.session.add(new_post)
        db.session.commit()

        new_post_id = new_post.id

        flash('게시물이 생성되었습니다.', 'success')
        return redirect(url_for('posts.show_post', post_id=new_post_id))

    return render_template('product/make-post.html', form=form, current_user=current_user,
                               logged_in=current_user.is_authenticated)


@posts.route('/edit/<string:post_id>', methods=['GET', 'POST'])
@is_author
def edit(post_id):
    """
    기존 게시물을 수정하는 함수

    - 작성자만 접근 가능
    - 이미지 추가/삭제
    - 게시물 내용 수정

    Parameters:
        post_id (str): 수정할 게시물의 ID

    Returns:
        template: 게시물 수정 페이지 또는 수정된 게시물로 리다이렉트
    """
    post = db.get_or_404(Post, post_id)
    form = CreatePostForm(
        title=post.title,
        price=post.price,
        textarea=post.body,
        category=post.category
    )
    
    if request.method == "POST":
        post.title = form.title.data
        post.price = form.price.data
        post.category = form.category.data
        post.body = form.textarea.data

        current_images = post.img_url.split(',') if post.img_url else []
        
        delete_images = request.form.getlist('deleteImages')

        if delete_images:
            for img_url in delete_images:
                public_id = img_url.split('/')[-1].split('.')[0]
                cloudinary.uploader.destroy(f"Products/{public_id}")
                
                if img_url in current_images:
                    current_images.remove(img_url)
            
            post.img_url = ','.join(current_images)

        files = request.files.getlist('files')
        
        if files and files[0].filename != '':
            invalid_files = [file.filename for file in files if not allowed_file(file.filename)]
            
            if invalid_files:
                flash(f"허용되지 않은 파일 형식: {', '.join(invalid_files)}", 'danger')
                return redirect(url_for('posts.edit', post_id=post_id))
            
            for file in files:
                response = cloudinary.uploader.upload(file, folder="Products")
                img_url = response['secure_url']
                current_images.append(img_url)
                
            post.img_url = ','.join(current_images)
            
        db.session.commit()

        flash('게시물이 수정되었습니다.', 'success')
        return redirect(url_for('posts.show_post', post_id=post_id))
        
    return render_template('product/edit-post.html', form=form, post=post,
                         logged_in=current_user.is_authenticated)


@posts.route('/delete/<string:post_id>', methods=['GET', 'POST'])
@is_author
def delete(post_id):
    """
    게시물을 삭제하는 함수

    - 작성자만 접근 가능
    - 관련 이미지 삭제
    - 관련 좋아요 데이터 삭제

    Parameters:
        post_id (str): 삭제할 게시물의 ID

    Returns:
        redirect: 게시물 목록 페이지
    """
    post_to_delete = db.get_or_404(Post, post_id)
    current_images = post_to_delete.img_url.split(',')

    for img_url in current_images:
        public_id = img_url.split('/')[-1].split('.')[0]
        cloudinary.uploader.destroy(f"Products/{public_id}")

    if Like.query.filter(Like.post_id == post_id).count() > 0:
        Like.query.filter(Like.post_id == post_id).delete()

    db.session.delete(post_to_delete)
    db.session.commit()

    flash('게시물이 삭제되었습니다.', 'success')
    return redirect(url_for('posts.all_products'))