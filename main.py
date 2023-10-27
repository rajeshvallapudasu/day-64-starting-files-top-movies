from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os


db=SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
# app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top_movies.db"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///top_movies.db")
db.init_app(app)


api_key="6ba024389e182f5ab72eed16c5950092"
MOVIE_DB_INFO_URL="https://api.themoviedb.org/3/search/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2YmEwMjQzODllMTgyZjVhYjcyZWVkMTZjNTk1MDA5MiIsInN1YiI6IjY1MmI0MDVlMDI0ZWM4MDBhZWNiODBjZCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.XZO_GdaRWOMw0LP9uyv_JiHF80fehxyCFyGePt3Dj1c"
}




class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.Integer,nullable=False)
    description=db.Column(db.String,nullable=False)
    rating=db.Column(db.Float,nullable=False)
    ranking=db.Column(db.Integer,nullable=False)
    review=db.Column(db.String,nullable=False)
    img_url=db.Column(db.String,nullable=False)




Bootstrap5(app)
class RateMovie(FlaskForm):
    rating = StringField('rating', validators=[DataRequired()])
    review = StringField("review", validators=[DataRequired()])
    submit = SubmitField('Done')
class AddMovie(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')



@app.route("/")
def home():
    all_movies = []

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form=RateMovie()
    movie_id = request.args.get('id')
    movie = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalar()
    if form.validate_on_submit():
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", form=form,movie=movie)


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')

    # DELETE A RECORD BY ID
    movie = db.session.execute(db.select(Movie).where(Movie.id==movie_id)).scalar()
    # Alternative way to select the book to delete.
    # book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add",methods=["GET", "POST"])
def add():
    form=AddMovie()
    if form.validate_on_submit():
        movie_name=form.title.data
        response = requests.get(MOVIE_DB_INFO_URL, params={"api_key": api_key, "query": movie_name})
        data = response.json()["results"]
        return render_template("select.html", options=data)

    return render_template("add.html", form=form)
@app.route("/find")
def find_movie():
    movie_api_id=request.args.get("id")
    if movie_api_id:
        url = f"https://api.themoviedb.org/3/movie/{movie_api_id}?language=en-US"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2YmEwMjQzODllMTgyZjVhYjcyZWVkMTZjNTk1MDA5MiIsInN1YiI6IjY1MmI0MDVlMDI0ZWM4MDBhZWNiODBjZCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.XZO_GdaRWOMw0LP9uyv_JiHF80fehxyCFyGePt3Dj1c"
        }
        response = requests.get(url, headers=headers)
        data=response.json()

        new_movie=Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"],
            rating=9.5,
            ranking = 10,
            review="good film"
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=False)
