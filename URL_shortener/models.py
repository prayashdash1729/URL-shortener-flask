from datetime import datetime
from URL_shortener import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(120), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    links = db.relationship('Links', backref='author', lazy=True)
    clicks = db.relationship('Clicks', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Links(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    long_url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(6), nullable=False)
    date_created_utc = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    times_clicked = db.Column(db.Integer, nullable=False, default=0)
    clicks = db.relationship('Clicks', backref='link', lazy=True)

    def __repr__(self):
        return f"Links('{self.user_id}', '{self.long_url}', '{self.short_url}', '{self.date_created_utc}')"


class Clicks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('links.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # ip address of the user who clicked the link
    ip_address = db.Column(db.String(20), nullable=False)
    date_clicked_utc = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Clicks('{self.link_id}', '{self.user_id}', '{self.ip_address}', '{self.date_clicked_utc}')"
