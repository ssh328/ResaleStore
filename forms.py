from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, IntegerField, TextAreaField
from wtforms.fields.choices import SelectField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Email, NumberRange, Length

# bleach: Html을 정리하고, XSS 공격을 방지하는 라이브러리
import bleach

# 사용자 정의 유효성 검사, 입력값에서 HTML 태그를 제거
def escape_html(form, field):
    # bleach.clean: 입력값에서 HTML 태그를 제거, Strip=True: 모든 태그 제거
    clean_data = bleach.clean(field.data, strip=True)
    # HTML 태그가 포함된 경우, 에러 발생
    if clean_data != field.data:
        raise ValueError("Invalid input detected.")
    field.data = clean_data


# SIGNUP FORM
class SignUpForm(FlaskForm):
    first_name = StringField(validators=[DataRequired()])
    last_name = StringField(validators=[DataRequired()])
    name = StringField(validators=[DataRequired()]) # validators: 유효성 검사
    password = PasswordField(validators=[DataRequired(), Length(min=8)])
    email = EmailField(validators=[DataRequired()])
    submit = SubmitField('Log In')


# LOGIN FORM
class LoginForm(FlaskForm):
    password = PasswordField(validators=[DataRequired(), Length(min=8)])
    email = EmailField(validators=[DataRequired()])
    submit = SubmitField('Log In')


class CreatePostForm(FlaskForm):
    title = StringField("제목", validators=[DataRequired()])
    price = IntegerField("가격", validators=[DataRequired(), NumberRange(min=0, max=1000000000)])
    textarea = StringField("자세한 설명", widget=TextArea(), validators=[DataRequired(), escape_html])
    category = SelectField("카테고리",
        choices=[
            ("", "카테고리 선택"),
            ("디지털기기", "디지털기기"),
            ("생활가전", "생활가전"),
            ("가구/인테리어", "가구/인테리어"),
            ("생활/주방", "생활/주방"),
            ("유아동", "유아동"),
            ("유아도서", "유아도서"),
            ("여성의류", "여성의류"),
            ("여성잡화", "여성잡화"),
            ("남성패션/잡화", "남성패션/잡화"),
            ("뷰티/미용", "뷰티/미용"),
            ("스포츠/레저", "스포츠/레저"),
            ("취미/게임/음반", "취미/게임/음반"),
            ("도서", "도서"),
            ("티켓/교환권", "티켓/교환권"),
            ("가공식품", "가공식품"),
            ("건강기능식품", "건강기능식품"),
            ("반려동물용품", "반려동물용품"),
            ("식물", "식물"),
            ("기타 중고물품", "기타 중고물품"),
        ],
        validators=[DataRequired()])
    submit = SubmitField("등록")


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField(validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("변경")