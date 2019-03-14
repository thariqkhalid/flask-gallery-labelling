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

GALLERY_PATH = 'static/gallery/'
engine = db.create_engine('sqlite:///trafficlabelling.db')

def create_gallery_files(gallery_path):

    glry_files = os.listdir(gallery_path)
    GALLERY_FILES = [os.path.join(gallery_path, i) for i in glry_files]

    print("Checking for Obscene content............")
    final_gallery_files = []
    for i,image_path in enumerate(GALLERY_FILES):

        ext = image_path.split(".")[-1]
        print("extension {}".format(ext))
        if ext != "mp4":
            print("predicting nsfw for image {}".format(image_path))
            res = predict_nsfw(image_path)
            if res == "sfw":
                screen_res = detect_screenshot_phone(image_path)
                if screen_res:
                    final_gallery_files.append(glry_files[i])

        else:
            final_gallery_files.append(glry_files[i])

    return final_gallery_files


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