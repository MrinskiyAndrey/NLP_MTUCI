from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from os import environ
import fasttext

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
db = SQLAlchemy(app)

PATH_TO_MODEL = "/app/models/"
MODEL_NAME = "1_model_1.bin"

TEMP_FILE = "/app/tmp.txt"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    like = db.Column(db.String, nullable=True)


db.create_all()


def get_last_model(path_to_model: str):
    import glob
    import os

    list_of_files = glob.glob(f'{path_to_model}*.bin')
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        comment = request.form['comment']
        try:
            like = request.form['like']
        except:
            like = None

        if request.form['btn'] == 'to_ml':

            last_file = get_last_model(PATH_TO_MODEL)
            model = fasttext.load_model(last_file)
            print("Идет распознование текста...")
            pred_raw = model.predict(comment)
            pred = pred_raw[0][0]
            if pred == '__label__negative':
                res = 'negative'
            else:
                res = 'positive'
            return render_template('index.html', retry_comment=comment, ml_result=res)

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
            conn = psycopg2.connect(dbname="postgres", user="postgres", password="postgres", host="flask_db")
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM public.post")
            rows = cursor.fetchall()

            cursor.close()  # закрываем курсор
            conn.close()  # закрываем подключение

            rows_prep = [f"__label__{row[2]} {row[1]}\n" for row in rows]
            with open(TEMP_FILE, 'w') as fp:
                fp.writelines(rows_prep)

            last_file = get_last_model(PATH_TO_MODEL)

            pretrained_model = fasttext.load_model(last_file)

            # Дообучение модели
            pretrained_model.quantize(input=TEMP_FILE, retrain=True)
            print("Идет дообучение модели...")
            import time

            pretrained_model.save_model(f'{PATH_TO_MODEL}{str(time.time()).split(".")[0]}.bin')

            return render_template('index.html')

    else:
        return render_template("index.html")
