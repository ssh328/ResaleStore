from dotenv import load_dotenv
import os
from flask import render_template, url_for, request, redirect, flash, jsonify, Blueprint
from datetime import datetime
from flask_login import current_user
from model.data import Post, db, Like
from forms import CreatePostForm
from securityyy.security import admin_only, is_author
from cloudinary_dir.cloudinary import cloudinary
import cloudinary.uploader

load_dotenv()
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# 파일 확장자 확인
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 게시물 검색
def search_posts(query):
    # Post.title.contains(query): 게시물 제목에 쿼리 포함된 게시물 찾기
    return db.select(Post).filter(Post.title.contains(query)).order_by(Post.date.desc())

# 게시물 블루프린트 생성
posts = Blueprint('posts', __name__, template_folder='templates/product')


# 모든 게시물 보여주는 창
@posts.route('/all-products', methods=['GET', "POST"])
def all_products():
    categories = [
        "디지털기기", "생활가전", "가구/인테리어", "생활/주방", "유아동", "유아도서",
        "여성의류", "여성잡화", "남성패션/잡화", "뷰티/미용", "스포츠/레저", "취미/게임/음반",
        "도서", "티켓/교환권", "가공식품", "건강기능식품", "반려동물용품", "식물", "기타 중고물품"
    ]

    # 현재 로그인 한 유저가 좋아요 누른 게시물 id 목록을 가져옴
    like_posts = []
    if current_user.is_authenticated:
        like_posts = [like.post_id for like in current_user.likes]

    # request.args.get(): URL 쿼리 문자열에서 특정 매개변수 값을 가져오는 데 사용, 사용자가 GET 요청을 보낼 때 URL에 포함된 매개변수를 출력
    page = request.args.get('page', 1, type=int)

    # 필터링 기능
    # 필터 초기화 시 default 값으로 url에서 category와 sort_by query 값 보이지 않게 함
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

    # 0이 False로 간주되기 때문에 명시적으로 None값인지 확인해야 함
    if start_price is not None and end_price is not None:
        query = query.filter(Post.price.between(start_price, end_price))

    # 검색 쿼리 추가
    search_query = request.args.get('search', default=None)
    if search_query:
        # search_posts 함수를 사용하여 게시물 검색
        query = search_posts(search_query)

    posts = db.paginate(query, page=page, per_page=20, error_out=False)
        # db.paginate(): 특정 페이지에 해당하는 데이터만 선택하고 Pagination 을 구현
        # page: 현재 페이지의 번호롤 나타냄
        # per_page: 한 페이지에 표시할 항목의 개수
        # error_out: 만약 True 로 설정되면, 존재하지 않는 페이지에 접근할 때 404 오류를 발생

        # data = db.session.execute(db.select(Post)).scalars().all()
        # 모든 데이터를 한 번에 불러올 수 있지만 Pagination 이 적용 되지 않음

    return render_template(
        'product/all-products.html',
        all_data=posts.items,  # 현재 페이지에 해당하는 게시물들이 담겨있음
        logged_in=current_user.is_authenticated,
        pagination=posts,
        like_posts=like_posts,
        categories=categories,
        category=category,
        sort_by=sort_by,
        startPrice=start_price,
        endPrice=end_price
    )


# 게시물 클릭 시 그 게시물 내용 보여 주는 창
@posts.route('/post/<string:post_id>', methods=["GET", "POST"])
def show_post(post_id):
    # Post 모델에서 기본 키가 post_id 인 레코드를 조회하고, 존재하지 않으면 404 반환
    requested_post = db.get_or_404(Post, post_id)

    img_urls = requested_post.img_url.split(',') if requested_post.img_url else []

    return render_template('product/post.html', requested_post=requested_post,
                           logged_in=current_user.is_authenticated, img_urls=img_urls,
                           ADMIN_USER_ID=ADMIN_USER_ID)


# 새 게시물 생성하는 창
@posts.route('/new-products-post', methods=['GET', 'POST'])
@admin_only
def add_new_products_post():
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


# 게시물 수정
@posts.route('/edit/<string:post_id>', methods=['GET', 'POST'])
@is_author
def edit(post_id):
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

        # 기존 이미지 URL 목록을 가져옴
        current_images = post.img_url.split(',') if post.img_url else []
        
        # 삭제할 이미지 가져오기
        delete_images = request.form.getlist('deleteImages')

        if delete_images:
            # 삭제할 이미지 처리
            for img_url in delete_images:
                # Cloudinary에서 이미지 삭제
                public_id = img_url.split('/')[-1].split('.')[0]
                cloudinary.uploader.destroy(f"Products/{public_id}")
                
                # 현재 이미지 목록에서 삭제된 이미지 제거
                if img_url in current_images:
                    current_images.remove(img_url)
            
            # 남은 이미지들을 다시 문자열로 결합하여 저장
            post.img_url = ','.join(current_images)

        # 새 이미지 업로드
        files = request.files.getlist('files')
        
        if files and files[0].filename != '':
            invalid_files = [file.filename for file in files if not allowed_file(file.filename)]
            
            if invalid_files:
                flash(f"허용되지 않은 파일 형식: {', '.join(invalid_files)}", 'danger')
                return redirect(url_for('posts.edit', post_id=post_id))
            
            # 새 이미지 업로드
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


# 게시물 삭제
@posts.route('/delete/<string:post_id>', methods=['GET', 'POST'])
@is_author
def delete(post_id):
    post_to_delete = db.get_or_404(Post, post_id)
    current_images = post_to_delete.img_url.split(',')

    # 이미지 삭제
    for img_url in current_images:
        public_id = img_url.split('/')[-1].split('.')[0]
        cloudinary.uploader.destroy(f"Products/{public_id}")

    # 좋아요가 있는 경우에만 삭제
    if Like.query.filter(Like.post_id == post_id).count() > 0:
        Like.query.filter(Like.post_id == post_id).delete()

    # 게시물 삭제
    db.session.delete(post_to_delete)
    db.session.commit()

    flash('게시물이 삭제되었습니다.', 'success')
    return redirect(url_for('posts.all_products'))