from flask import Flask, render_template, request, url_for, redirect
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import sqlite3
import numpy as np
import os


currentdirectory = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
model_path = "InceptionResNetV2_Model.h5"
model = load_model(model_path)
category = {0: "Bacterial Leaf Blight", 1: "Brown Spot", 2: "Leaf Smut"}


def model_predict(image_path, model):
    print(image_path)
    image = load_img(image_path, target_size=(224, 224))
    image = img_to_array(image)
    image = image/255
    image = np.expand_dims(image, axis=0)
    result = np.argmax(model.predict(image))
    if result == 0:
        return "Bacterial Leaf Blight", "BacterialLeafBlight.html"
    elif result == 1:
        return "Brown Spot", "BrownSpot.html"
    elif result == 2:
        return "Leaf Smut", "LeafSmut.html"


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/signup")
def signup():
    name = request.args.get("name")
    username = request.args.get("username")
    password = request.args.get("psw")
    email = request.args.get("email")
    contact = request.args.get("CN")
    connection = sqlite3.connect(currentdirectory + "\database.db")
    cursor = connection.cursor()
    query = "INSERT INTO User VALUES ('{n}','{un}','{p}','{e}',{c})".format(n=name, un=username, p=password, e=email, c=contact)
    cursor.execute(query)
    connection.commit()
    connection.close()
    return render_template("login.html")


@app.route("/signin")
def signin():
    username = request.args.get("username")
    password = request.args.get("psw")
    connection = sqlite3.connect(currentdirectory + "\database.db")
    cursor = connection.cursor()
    query = "SELECT Username, Password FROM User WHERE Username='{un}' AND Password='{p}'".format(un=username, p=password)
    result = cursor.execute(query)
    result = result.fetchone()
    if result is None:
        return render_template("login.html")
    elif username == result[0] and password == result[1]:
        return render_template("index.html")
    else:
        return render_template("login.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        file = request.files['image']
        filename = file.filename
        file_path = os.path.join('static/user uploaded', filename)
        file.save(file_path)
        pred, output_page = model_predict(file_path, model)
        return render_template(output_page, pred_output=pred, user_image=file_path)


if __name__ == "__main__":
    app.run(debug=True)
