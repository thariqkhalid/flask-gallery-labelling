import sqlalchemy as db
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import os, sys
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
import re

GALLERY_PATH = '/Users/thariq/galleries/flask-simple-image-gallery/static/gallery/'
engine = db.create_engine('sqlite:////Users/thariq/galleries/flask-simple-image-gallery/trafficlabelling.db')

def create_gallery_files():
    glry_files = os.listdir(GALLERY_PATH)
    #GALLERY_FILES = [os.path.join(GALLERY_PATH,i) for i in glry_files]
    return glry_files


def insert_data_db():
    connection, traffic = get_connection()
    gallery_files = create_gallery_files()
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
    res = insert_data_db()
    if res == 1:
        print("Successfully created the database and inserted the files into table Traffic")