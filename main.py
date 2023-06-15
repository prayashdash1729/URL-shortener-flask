from flask import Flask, render_template, request, redirect, flash, url_for
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import random

with open("templates/URLs.json", "r") as c:
    links = json.load(c)["links"]
c.close()

with open("templates/config.json", "r") as f:
    params = json.load(f)["params"]
f.close()


def generate_short_url(length=6):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    short_url = ""
    while short_url in links.keys() or short_url == "":
        short_url = "".join(random.choice(chars) for _ in range(length))
    return short_url


app = Flask(__name__)

app.config['SECRET_KEY'] = '182f5606c7f67d4aded0b793195fb171'

@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        long_url = request.form.get("long_url")
        short_url = generate_short_url()
        print(short_url)
        links[short_url] = long_url
        with open("templates/URLs.json", "w") as f:
            json.dump({"links": links}, f)
        f.close()

        return render_template("index.html", short_url=params["HOST"] + short_url, show=True)

    return render_template("index.html", short_url="", show=False)


@app.route("/<short_url>")
def redirect_to_url(short_url):
    if short_url in links.keys():
        return redirect(links[short_url])
    else:
        return render_template("404.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for new user {form.username.data}!", "success")
        return redirect(url_for("home"))
    return render_template("signup.html", title='Sign Up', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form  = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@admin.com' and form.password.data == 'admin':
            flash(f"Logged in as {form.email.data}!", "success")
            return redirect(url_for("home"))
        else:
            flash(f"Login unsuccessful. Please check your email and password.", "danger")
    return render_template("login.html", title='Sign In', form=form)


if __name__ == "__main__":
    app.run(debug=True)
