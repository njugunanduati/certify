import os
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from flask_weasyprint import HTML, render_pdf
from app.forms import LoginForm, SignUpForm, ResetPasswordForm, ChangePasswordForm
from app.models import User, Course, UserCourse
from app.email import send_confirm_email, send_password_reset_email
from app import db
from app import app

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
BASE_DIR = app.root_path
IMAGE_PATH = BASE_DIR + app.config['UPLOAD_FOLDER']
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    template_name = 'login.html'
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template(template_name, title='Sign In', form=form)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignUpForm()
    template_name = 'register.html'
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        course = Course.query.get(1)
        user_course = UserCourse(
            user_id=user.id,
            course_id=course.id
        )
        db.session.add(user_course)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template(template_name, title='Register', form=form)



@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    template_name = 'reset_password_request.html'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            user.change_password = 1
            user.password = None
            db.session.commit()
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    template_name = 'reset_password.html'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.change_password = 0
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template(template_name, form=form)


@app.route('/index')
@login_required
def index():
    template_name = 'index.html'
    user = User.query.get(current_user.id)
    return render_template(template_name, user=user)


@app.route('/print_certificate/')
@login_required
def print_certificate():
    template_name = 'certificate.html'
    # Make a PDF straight from HTML in a string.
    user = User.query.get(current_user.id)
    name = '{} {}'.format(user.first_name, user.last_name)
    user_course = UserCourse.query.filter_by(user_id=user.id).first()
    course = Course.query.get(user_course.course_id)
    course_name = course.name
    html = render_template(template_name, name=name, course=course_name)
    return render_pdf(HTML(string=html))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))