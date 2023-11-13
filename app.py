from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from os import environ


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    like = db.Column(db.String, nullable=True)


db.create_all()


@app.route("/", methods=['POST', 'GET'])
def index():
    #post = Post.query
    if request.method == 'POST':
        comment = request.form['comment']
        try:
            like = request.form['like']
        except:
            like = None

        if request.form['btn'] == 'to_ml':
            try:
                print(comment)
                return render_template('index.html', retry_comment=comment)

            except:
                return "Ошибка при обращении к ML!"

        elif request.form['btn'] == 'to_bd':
            post = Post(comment=comment, like=like)
            try:
                db.session.add(post)
                db.session.commit()
                return render_template("index.html")
            except:
                return "Ошибка при обращении к базе данных!"
    else:
        return render_template("index.html")
