"""
This module aims to create a model having the filesystem as backend, since
if someone don't want to add extra metadata more than the metadata given
by the file informations is useless to use a database.

TODO: traverse directory.
"""
from werkzeug import secure_filename

import os
from createdb import get_image_filepaths


class FilesystemObjectDoesNotExist(Exception):
    pass

class FilesystemObject(object):
    def __init__(self, filename, post=None, root='static/gallery/'):
        """Create an object from the information of the given filename or from a
        uploaded file.

        Example of usage:

            if request.method == 'POST' and 'photo' in request.POST:
                f = FilesystemObject('cats.png', request.POST['photo'])

        """
        self.root_dir = root
        self.filename = filename if not post else secure_filename(post.filename)
        self.abspath  = os.path.join(self.root_dir, filename)
        # self.abspath = self.filename

        if post:
            self.upload(post)

        try:
            stats = os.stat(self.abspath)
        except IOError as e:
            raise FilesystemObjectDoesNotExist(e.message)

        self.timestamp = stats.st_mtime

    def upload(self, post):
        """Get a POST file and save it to the settings.GALLERY_ROOT_DIR"""
        # TODO: handle filename conflicts
        # http://flask.pocoo.org/docs/patterns/fileuploads/
        post.save(os.path.join(self.root_dir, self.filename))
        # post.save(self.filename)

    @classmethod
    def all(cls, user_id):
        """Return a list of files contained in the directory pointed by settings.GALLERY_ROOT_DIR.
        """
        images_list = []
        videos_list = []
        images_list, videos_list = get_image_filepaths(user_id)
        print(images_list, videos_list)
        images = [cls(x) for x in images_list]
        videos = [cls(x) for x in videos_list]
        return images, videos

        # return [cls(x) for x in os.listdir(root)] #original code

class Image(FilesystemObject):
    pass

