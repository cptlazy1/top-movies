from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top-movies.db'
Bootstrap(app)

# CREATE DB
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String(250), nullable=True)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

class MovieForm(FlaskForm):
    rating = StringField('Your Rating', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Done')

class AddMovieForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    year = StringField('Year', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    rating = StringField('Rating', validators=[DataRequired()])
    ranking = StringField('Ranking', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    img_url = StringField('Image URL', validators=[DataRequired()])
    submit = SubmitField('Add Movie')

# CREATE TABLE
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.rating.desc()))
    all_movies = result.scalars().all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = i + 1
    db.session.commit()
    return render_template("index.html", all_movies=all_movies)

@app.route("/edit/<int:movie_id>", methods=["GET", "POST"])
def edit(movie_id):
    movie = db.get_or_404(Movie, movie_id)
    form = MovieForm(request.form, obj=movie)
    if request.method == "POST":
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)

@app.route("/delete/<int:movie_id>", methods=["GET", "POST"])
def delete(movie_id):
    movie_to_delete = db.get_or_404(Movie, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddMovieForm()
    if request.method == "POST":
        new_movie = Movie(
            title = request.form["title"],
            year = int(request.form["year"]),
            description = request.form["description"],
            rating = float(request.form["rating"]),
            ranking = int(request.form["ranking"]),
            review = request.form["review"],
            img_url = request.form["img_url"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add.html", form=form)


if __name__ == '__main__':
    app.run(debug=True)
