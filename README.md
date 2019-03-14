# flask-gallery-labelling

**Create a new virtual environment with**

  `conda create -n flaskdb`
  
**Install the requirements file**

  `pip install -r requirements.txt`

**Steps** for setting up the Database
1. Run `python createdb.py --gallery_path "static/gallery/" `

Copy all the images & videos to static/gallery folder


2. Run `python create_users_db.py`
3. Run `python app.py`
4. Go to http://localhost:8000 and login with any of the three username and password
