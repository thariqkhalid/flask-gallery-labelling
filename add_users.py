import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_users_db import *

engine = create_engine('sqlite:////Users/thariq/galleries/flask-simple-image-gallery/trafficlabelling.db', echo=True)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

user = User("user1", "password")
session.add(user)

user = User("user2", "python")
session.add(user)

user = User("user3", "python")
session.add(user)

# commit the record the database
session.commit()

session.commit()