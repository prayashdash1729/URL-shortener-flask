from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import login_user, current_user, logout_user, login_required
from URL_shortener import app, db, bcrypt
from URL_shortener.models import User, Links
from URL_shortener.forms import RegistrationForm, LoginForm
import json
import random


with open("URLs.json", 'r') as c:
    links = json.load(c)["links"]
c.close()

with open("config.json", 'r') as f:
    params = json.load(f)["params"]
f.close()


def generate_short_url(length=6):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    short_url = ""
    while short_url in links.keys() or short_url == "":
        short_url = "".join(random.choice(chars) for _ in range(length))
    return short_url


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        long_url = request.form.get("long_url")
        short_url = generate_short_url()
        print(short_url)
        links[short_url] = long_url
        with open("URLs.json", "w") as f:
            json.dump({"links": links}, f)
        f.close()

        return render_template("home.html", short_url=params["HOST"] + short_url, show=True)

    return render_template("home.html", short_url="", show=False)


@app.route("/<short_url>")
def redirect_to_url(short_url):
    if short_url in links.keys():
        return redirect(links[short_url])
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
    form  = LoginForm()
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
    return redirect(url_for("home"))
