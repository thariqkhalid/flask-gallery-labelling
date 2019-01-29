from flask import Blueprint, render_template, request, current_app, session
import simplejson
from .models import Image

# Static files only work for blueprints registered with url_prefix
gallery = Blueprint('gallery', __name__, template_folder='templates', static_folder='static')


# Working code
@gallery.route('/', methods=['GET', 'POST'])
def show_gallery():
    user_id = current_app.config['current_user']
    images, videos = Image.all(user_id)
    if images:
        return render_template('images.html', images=images)
    elif videos:
        return render_template('videos.html', videos=videos)
    else:
        return "Thank you!! You have completed the labeling succesfully"