"""Models for flask-feedback."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)


class User(db.Model):
    """Site user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(
        db.String(20),
        nullable=False,
        unique=True
    )
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)

    #feedback = db.relationship("Feedback", backref="user", cascade="all,delete")

    # start of convenience class methods

    @classmethod
    def register(cls, username, password, first_name):
        """Register a user, hashing their password."""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        user = cls(
            username=username,
            password=hashed_utf8,
            first_name=first_name
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class SavedBeer(db.Model):

    __tablename__ = "beers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    beer_id = db.Column(db.Text)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    ibu = db.Column(db.Text)
    abv = db.Column(db.Text)
    style = db.Column(db.Text)
    style_description = db.Column(db.Text)

    user = db.relationship('User', backref="beers")

class RatedBeer(db.Model):

    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    beer_id = db.Column(db.Text)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    ibu = db.Column(db.Text)
    abv = db.Column(db.Text)
    style = db.Column(db.Text)
    style_description = db.Column(db.Text)
    rating = db.Column(db.Integer,default=0)
    notes = db.Column(db.Text)

    user = db.relationship('User', backref="ratings")


