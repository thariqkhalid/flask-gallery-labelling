import sqlalchemy as db
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import os, sys
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
import re
from classify_nsfw import predict_nsfw
import argparse
from skimage import io
from skimage import color
import numpy as np
import cv2
import shutil

import tensorflow as tf
from model import OpenNsfwModel, InputType
from image_utils import create_tensorflow_image_loader
from image_utils import create_yahoo_image_loader

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

GALLERY_PATH = 'static/gallery/'
engine = db.create_engine('sqlite:///trafficlabelling.db')

IMAGE_LOADER_TENSORFLOW = "tensorflow"
IMAGE_LOADER_YAHOO = "yahoo"

def create_gallery_files(gallery_path):

    glry_files = os.listdir(gallery_path)
    GALLERY_FILES = [os.path.join(gallery_path, i) for i in glry_files]

    model = OpenNsfwModel()

    with tf.Session() as sess:

        itype = InputType.TENSOR.name.lower()
        image_loader = IMAGE_LOADER_YAHOO

        input_type = InputType[itype.upper()]
        model.build(weights_path="open_nsfw-weights.npy", input_type=input_type)

        sess.run(tf.global_variables_initializer())

        print("Checking for Obscene content............")
        final_gallery_files = []

        def predict_nsfw_faster(image, sess):

            predictions = \
                sess.run(model.predictions,
                         feed_dict={model.input: image})

            sfw_score = predictions[0][0]

            print("\tSFW score:\t{}".format(predictions[0][0]))
            print("\tNSFW score:\t{}".format(predictions[0][1]))

            if sfw_score > 0.94:
                return "sfw"
            else:
                return "nsfw"

        def get_tf_image(image_path):
            if input_type == InputType.TENSOR:
                if image_loader == IMAGE_LOADER_TENSORFLOW:
                    fn_load_image = create_tensorflow_image_loader(tf.Session(graph=tf.Graph()))
                else:
                    fn_load_image = create_yahoo_image_loader()
            elif input_type == InputType.BASE64_JPEG:
                import base64
                fn_load_image = lambda filename: np.array([base64.urlsafe_b64encode(open(image_path, "rb").read())])

            print("predicting nsfw for image {}".format(image_path))

            image = fn_load_image(image_path)
            return image

        for i, image_path in enumerate(GALLERY_FILES):

            fn_load_image = None
            ext = image_path.split(".")[-1]
            print("extension {}".format(ext))

            if ext != "mp4":

                # print("predicting nsfw for image {}".format(image_path))
                image = get_tf_image(image_path)
                res = predict_nsfw_faster(image, sess)
                if res == "sfw":
                    screen_res = detect_screenshot_phone(image_path)
                    if screen_res:
                        final_gallery_files.append(glry_files[i])
                else:
                    image_name = image_path.split("/")[-1]
                    cwd = os.getcwd()
                    print("cwd =", cwd)
                    wd = os.path.join(cwd, "static/nsfw/")
                    image_name = os.path.join(wd, image_name)
                    print("image name for nsfw:", image_name)
                    shutil.copy(image_path, image_name)

            elif ext == "mp4":
                frame = detect_nsfw_video_frame(image_path)
                image = get_tf_image(frame)
                res = predict_nsfw_faster(image, sess)
                if res == "sfw":
                    screen_res = detect_screenshot_phone(frame)
                    if screen_res:
                        final_gallery_files.append(glry_files[i])
                else:
                    image_name = image_path.split("/")[-1]
                    cwd = os.getcwd()
                    print("cwd =", cwd)
                    wd = os.path.join(cwd, "static/nsfw/")
                    image_name = os.path.join(wd, image_name)
                    print("image name for nsfw:", image_name)
                    shutil.copy(image_path, image_name)

            else:
                final_gallery_files.append(glry_files[i])

    return final_gallery_files

def detect_nsfw_video_frame(video_path):
    capture = cv2.VideoCapture(video_path)
    frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    capture.set(cv2.CAP_PROP_POS_FRAMES, np.random.randint(0, frame_count))
    _, frame = capture.read()
    fname = "static/video_frames/frame.jpg"
    status = cv2.imwrite(fname, frame)

    if status == True:
        return fname


def detect_screenshot_phone(image_path):
    # Find out the min and max of the peaks and find the longest stretch of horizontal line.
    # It should be in the middle

    img_rgb = io.imread(image_path)
    img_gray = color.rgb2gray(img_rgb)
    grayvsum = np.cumsum(img_gray, axis=0)
    gray_cumsum_v = grayvsum[50, :]
    gray_cumsum_v = gray_cumsum_v.tolist()

    l = len(gray_cumsum_v)
    print("length of the image:", l)
    mid = int(l / 2)
    total_range = 0

    average = int(np.mean(gray_cumsum_v))
    range_values = gray_cumsum_v[200:300]
    min_range = np.min(range_values)
    max_range = np.max(range_values)

    print("min range: ", min_range)
    print("max range:", max_range)

    print("average_range: ",average)

    print(gray_cumsum_v[mid])
    if gray_cumsum_v[mid] == average:
        print("not a screenshot")
        return 1

    if (min_range + 2) < max_range:
        print("not a screenshot")
        return 1


    if l < 300:
        return 1

    for i in range(200, 300):
        total_range = total_range + gray_cumsum_v[i]

    average = int(total_range / 100)
    mid_range = int(gray_cumsum_v[250])

    print("average:", average)
    print("mid_range:", mid_range)

    if average == mid_range:
        print("screenshot detected")
        return 0
    else:
        print("not a screenshot")
        return 1


def insert_data_db(gallery_path):
    connection, traffic = get_connection()
    gallery_files = create_gallery_files(gallery_path)
    custom_dict = [{'filename': value} for value in gallery_files]
    connection.execute(traffic.insert(), custom_dict)
    return 1


def get_connection():
    connection = engine.connect()
    metadata = db.MetaData()
    try:
        traffic = db.Table('traffic', metadata, autoload=True, autoload_with=engine)
    except:
        traffic = Table('traffic', metadata,
                        Column('id', Integer, primary_key = True),
                        Column('filename', String),
                        Column('user1', Integer),
                        Column('user2', Integer),
                        Column('user3', Integer),
                        Column('user4', Integer),
                        Column('user5', Integer),
                        Column('user6', Integer),
                        Column('user7', Integer),
                        Column('user8', Integer),
                        Column('user9', Integer),
                        Column('user10', Integer)
                        )
        metadata.create_all(engine)

    return connection, traffic


def get_image_filepaths(user_id):
    connection, traffic = get_connection()
    s = select([traffic])
    result = connection.execute(s)
    imgs = []
    vds = []
    for row in result:
        if row[user_id] is None:
            ext = row[1].split(".")[1]
            if ext == "jpeg" or ext == "jpg" or ext == "png":
                imgs.append(row[1])
            elif ext == "mp4":
                vds.append(row[1])
                print("Videos present \n")

    return imgs, vds


def update_img_label(img_filename, label_value=1, user_id=0):
    connection, traffic = get_connection()
    user_id = int(re.search('\d+', user_id).group(0))

    if user_id == 1:
        update_statement = traffic.update().where(traffic.c.filename == img_filename).values(user1=label_value)
    if user_id == 2:
        update_statement = traffic.update().where(traffic.c.filename == img_filename).values(user2=label_value)
    if user_id == 3:
        update_statement = traffic.update().where(traffic.c.filename == img_filename).values(user3=label_value)
    if user_id == 4:
        update_statement = traffic.update().where(traffic.c.filename == img_filename).values(user4=label_value)
    if user_id == 5:
        update_statement = traffic.update().where(traffic.c.filename == img_filename).values(user5=label_value)
    if user_id == 6:
        update_statement = traffic.update().where(traffic.c.filename == img_filename).values(user6=label_value)
    if user_id == 7:
        update_statement = traffic.update().where(traffic.c.filename == img_filename).values(user7=label_value)
    if user_id == 8:
        update_statement = traffic.update().where(traffic.c.filename == img_filename).values(user8=label_value)
    if user_id == 9:
        update_statement = traffic.update().where(traffic.c.filename == img_filename).values(user9=label_value)
    if user_id == 10:
        update_statement = traffic.update().where(traffic.c.filename == img_filename).values(user10=label_value)

    connection.execute(update_statement)


def get_usernames_passwords():
    connection = engine.connect()
    metadata = db.MetaData()
    users = db.Table('users', metadata, autoload=True, autoload_with=engine)

    s = select([users])
    result = connection.execute(s)

    return result


def check_user_details_db(post_username, post_password):
    metadata = db.MetaData()
    users = db.Table('users', metadata, autoload=True, autoload_with=engine)
    session_i = sessionmaker(bind=engine)
    s = session_i()

    query = s.query(users).filter(users.c.username.in_([post_username]), users.c.password.in_([post_password]))
    result = query.first()

    if result:
        return 1
    else:
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gallery_path", help="path to the images and videos", type=str)
    args = parser.parse_args()

    res = insert_data_db(args.gallery_path)
    if res == 1:
        print("Successfully created the database and inserted the files into table Traffic")