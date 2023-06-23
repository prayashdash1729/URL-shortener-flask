from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import login_user, current_user, logout_user, login_required
from URL_shortener import app, db, bcrypt
from URL_shortener.models import User, Links
from URL_shortener.forms import URLForm, RegistrationForm, LoginForm, UpdateAccountForm
from PIL import Image
import json
import random
import secrets
import os

with open("URLs.json", 'r') as c:
    links = json.load(c)["links"]
c.close()

with open("config.json", 'r') as f:
    params = json.load(f)["params"]
f.close()


def generate_short_url(length=6):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    short_url = ""
    shorts = [link.short_url for link in Links.query.all()]
    while short_url in shorts or short_url == "":
        short_url = "".join(random.choice(chars) for _ in range(length))
    return short_url


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    form = URLForm()
    if form.validate_on_submit():
        long_url = form.long_url.data
        short_url = generate_short_url()
        link = Links(user_id=current_user.id, long_url=long_url, short_url=short_url)
        db.session.add(link)
        db.session.commit()
        flash(f"URL shortened successfully!", "success")
        return render_template("home.html", form=form, show=True, short_url=short_url, long_url=long_url)

    return render_template("home.html", form=form, show=False)


@app.route("/<short_url>")
def redirect_to_url(short_url):
    shorts = [link.short_url for link in Links.query.all()]
    if short_url in shorts:
        return redirect(Links.query.filter_by(short_url=short_url).first().long_url)
    else:
        return render_template("404.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        pwd_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=pwd_hash)
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for new user {form.username.data} ! Kindly log in with your credentials", "success")
        return redirect(url_for("login"))
    return render_template("signup.html", title='Sign Up', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for("home"))
        else:
            flash(f"Login unsuccessful. Please check your email and password.", "danger")
    return render_template("login.html", title='Sign In', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/assets/profile_pics', picture_fn)

    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_fn = save_picture(form.picture.data)
            current_user.image_file = picture_fn
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated", "success")
        return redirect(url_for("profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    img_file = url_for('static', filename='assets/profile_pics/' + current_user.image_file)
    return render_template("profile.html", title=current_user.username, img_file=img_file, form=form)


@app.route("/dashboard")
@login_required
def dashboard():

    return render_template("dashboard.html", title="Dashboard")
