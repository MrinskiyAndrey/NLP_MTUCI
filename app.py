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

ML_result = "Негативный"


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        comment = request.form['comment']
        try:
            like = request.form['like']
        except:
            like = None

        #postgresql://postgres:postgres@flask_db:5432/postgres

        if request.form['btn'] == 'to_ml':
            # try:
            #     print(comment)
            #     #ML_result = request.get_json(pass)
            #     return render_template('index.html', retry_comment=comment, ML_result=ML_result)
            #
            # except:
            #     return "Ошибка при обращении к ML!"
            conn = psycopg2.connect(dbname="postgres", user="postgres", password="postgres", host="flask_db")
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM public.post")
            rows = cursor.fetchall()

            cursor.close()  # закрываем курсор
            conn.close()  # закрываем подключение

            return render_template('index.html', retry_comment=comment, ml_result=rows)
        elif request.form['btn'] == 'to_bd':
            post = Post(comment=comment, like=like)
            try:
                db.session.add(post)
                db.session.commit()
                return render_template("index.html")
            except:
                return "Ошибка при обращении к базе данных!"

        elif request.form['btn'] == 'reset':
            return render_template("index.html")

        elif request.form['btn'] == 'to_learn':
            # try:
            #     print(comment)
            #     #ML_result = request.get_json(pass)
            #     return render_template('index.html', retry_comment=comment, ML_result=ML_result)
            #
            # except:
            #     return "Ошибка при обращении к ML!"
            conn = psycopg2.connect(dbname="postgres", user="postgres", password="postgres", host="flask_db")
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM public.post")
            rows = cursor.fetchall()

            cursor.close()  # закрываем курсор
            conn.close()  # закрываем подключение

            return render_template('index.html', retry_comment=comment, ml_result=rows)

    else:
        return render_template("index.html")