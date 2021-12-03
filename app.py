from flask import Flask, json, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow

import os 

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    genre = db.Column(db.String, nullable=False)
    mpaa_rating = db.Column(db.String)
    poster_image = db.Column(db.String, unique=True)

    def __init__(self, title, genre, mpaa_rating, poster_image):
        self.title = title
        self.genre = genre
        self.mpaa_rating = mpaa_rating
        self.poster_image = poster_image


class MovieSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'genre', 'mpaa_rating', 'poster_image')

movie_schema = MovieSchema()
multi_movie_schema = MovieSchema(many=True)


# POST endpoint
@app.route('/movie/add', methods=["POST"])
def add_movie():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be sent as JSON')
    
    post_data = request.get_json()
    title = post_data.get('title')
    genre = post_data.get('genre')
    mpaa_rating = post_data.get('mpaa_rating')
    poster_image = post_data.get('poster_image')

    if title == None:
        return jsonify("Error: You must provide a 'title' key")
    if genre == None:
        return jsonify("Error: You must provide a 'genre' key")

    new_record = Movie(title, genre, mpaa_rating, poster_image)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(movie_schema.dump(new_record))

@app.route('/movie/get', methods=["GET"])
def get_all_movies():
    all_records = db.session.query(Movie).all()
    return jsonify(multi_movie_schema.dump(all_records))

@app.route('/movie/get/<id>', methods=["GET"])
def get_movie_by_id(id):
    one_movie = db.session.query(Movie).filter(Movie.id).first()
    return jsonify(movie_schema.dump(one_movie))

@app.route('/movie/update/<id>', methods=["PUT"])
def update_movie_by_id(id):
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be sent as JSON')

    put_data = request.get_json()
    title = put_data.get('title')
    genre = put_data.get('genre')
    mpaa_rating = put_data.get('mpaa_rating')
    poster_image = put_data.get('poster_image')

    movie_to_update = db.session.query(Movie).filter(Movie.id == id).first()

    if title != None:
        movie_to_update.title = title
    if genre != None:
        movie_to_update.genre = genre
    if mpaa_rating != None:
        movie_to_update.mpaa_rating = mpaa_rating
    if poster_image != None:
        movie_to_update.poster_image = poster_image
    
    db.session.commit()

    return jsonify(movie_schema.dump(movie_to_update))

@app.route('/movie/delete/<id>', methods=["DELETE"])
def delete_movie_by_id(id):
    movie_to_delete = db.session.query(Movie).filter(Movie.id == id).first()
    db.session.delete(movie_to_delete)
    db.session.commit()
    return jsonify("Movie was deleted")

if __name__ == "__main__":
    app.run(debug=True)