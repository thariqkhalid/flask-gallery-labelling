# encoding:utf-8
import os
from flask import Flask, redirect, url_for, request, render_template, session, flash
from gallery.views import gallery
from createdb import update_img_label, check_user_details_db
import settings
import re
import json


ROOT_DIR = os.path.dirname(__file__)

UPLOAD_DIR = os.path.join(ROOT_DIR, 'uploads')
UPLOAD_ALLOWED_EXTENSIONS = (
    'jpg',
    'jpeg',
    'png',
    'gif',
)


app = Flask(__name__)
app.register_blueprint(gallery, url_prefix='/gallery')
app.config['GALLERY_ROOT_DIR'] = settings.GALLERY_ROOT_DIR
app.config['current_user'] = ""
current_user = ""


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    elif session.get('logged_in'):
        # global current_user
        # messages = json.dumps({"user_id": current_user})
        # session['messages'] = messages
        return redirect(url_for('gallery.show_gallery'))
    else:
        return "Hello Boss!"


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return render_template("logout.html")

@app.route("/next")
def next():
    session['logged_in'] = True
    return redirect(url_for('gallery.show_gallery'))


@app.route('/login', methods=['POST'])
def do_admin_login():
    post_username = request.form['username']
    post_password = request.form['password']

    if check_user_details_db(post_username, post_password):
        # global current_user
        app.config['current_user'] = post_username
        user_id = int(re.search('\d+', app.config['current_user']).group(0))
        print("User number {}".format(user_id))
        # print("{} logged in".format(current_user))
        return redirect(url_for('gallery.show_gallery'))
    else:
        flash('wrong password!')
    return home()


@app.route('/check_selected', methods=['GET', 'POST'])
def update_selected_image_db():
    print("going to update the db")
    if request.method == 'GET':
        post = request.args.get('post', 0, type=str)
        opt = request.args.get('x', 0, type=int)
        img_name = str(post)
        # global current_user
        # print(current_user)
        update_img_label(img_name, opt, app.config['current_user'])

        print("Update done. Please check DB for results")
    return redirect(url_for('gallery.show_gallery'))


if __name__ == '__main__':
    app.logger.info('Listening on http://localhost:8000')
    app.secret_key = os.urandom(12)
    app.run(port=8000, debug=True)
