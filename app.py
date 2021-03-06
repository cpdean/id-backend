#!/usr/bin/python
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import Response


from werkzeug import secure_filename
import os

import db

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['jpg'])

UPLOAD_FOLDER = db.image_store
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return redirect(url_for("post_list"))

@app.route("/upload",methods=['POST'])
def upload_file():
    encoded = request.form['file']
    decoded = encoded.decode("base64")
    p = db.Post()
    p.title = request.form['title']
    p.caption = "something something"
    p.image_data = decoded
    p.save()
    id_number = db.get_latest_post().post_id
    return url_for("show_image",post_id=id_number)



@app.route('/posts/',methods=['POST','GET'])
def post_list():
    if request.method == 'POST':
        p = db.Post()
        p.title = request.form['title']
        p.caption = request.form['caption']
        image = get_image(request)
        p.image_name = image.filename
        p.image_data = image.stream.read()
        p.save()
        return redirect(url_for("post_list"))

    elif request.method == 'GET':
        posts = db.Post().show()
        return render_template("posts.html", posts=posts )

#FILE HANDLING

def allowed_file(filename):
    return '.' in filename and\
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_image(r):
    image = r.files['file']
    if image and allowed_file(image.filename):
        return image

@app.route('/post/',methods=['POST','GET'])
def redirect_to_latest():
    return redirect(url_for("show_latest_post"))

@app.route('/post/latest',methods=['POST','GET'])
def show_latest_post():
    post = db.get_latest_post()
    return render_template("view_post.html", post=post )

@app.route('/post/<int:post_id>',methods=['POST','GET'])
def show_post(post_id=None):
    if request.method == 'POST':
        pass

    elif request.method == 'GET':
        post = db.Post(post_id)
        return render_template("view_post.html", post=post )

@app.route('/image/goat.jpg',methods=['POST','GET'])
def show_goat(post_id=None):
    if request.method == 'POST':
        pass

    elif request.method == 'GET':
        post = db.Post(post_id)
        data = open("test-data/goatgoat.jpg","rb").read()
        r = Response(data, status=200, mimetype='image/jpeg')
        return r

"""
@app.route('/image-filtered/<int:post_id>.jpg',methods=['POST','GET'])
def show_filtered_image(post_id=None):
    if request.method == 'POST':
        pass

    elif request.method == 'GET':
        post = db.Post(post_id)
        data = post.image_data
        murad_filter = filter.oldify
        data = murad_filter(data)
        r = Response(data, status=200, mimetype='image/jpeg')
        return r
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    app.debug = True if port == 5000 else False
    app.run(host="0.0.0.0",port=port)
