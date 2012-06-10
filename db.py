from datetime import datetime
from sqlite3 import dbapi2 as sqlite3

from os.path import exists
from os import makedirs
import os 
from werkzeug import secure_filename

import logging

from oldify import filter

db = "database"
image_store = os.path.join("static","image-store")
filtered_image_store = os.path.join("static","filtered-image-store")
schema = "schema.sql"

def open_database_connection():
    return sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)

def connect_db():
    if not exists(db):
        init_db()
    return open_database_connection()

def init_db():
    init_image_store()
    with open_database_connection() as conn:
        with open(schema) as s:
            c = conn.cursor()

            c.executescript(s.read())
            conn.commit()

def init_image_store():
    if not exists(image_store):
        makedirs(image_store)
    if not exists(filtered_image_store):
        makedirs(filtered_image_store)

def get_latest_post():
    with connect_db() as conn:
        query = conn.cursor().execute( """
                                        select *
                                        from
                                        Post
                                        order by
                                        date DESC
                                        limit 1;
                                        """)
        post_id,date,title,body,image_path = query.fetchone()
        post_id = int(post_id)
        return Post(post_id)
 


class Post:

    def __init__(self,post_id=None):
        if not post_id:
            self.date = datetime.now()
            self.title = "This is the title"
            self.body = "The body"
            self.post_id = None
            self.image_name = None
        else:
            with connect_db() as conn:
                c = conn.cursor()
                c.execute("""select post_id,date,title,body,image_path
                            from Post 
                            where post_id = (?)""", (post_id,))

                post_id,date,title,body,image_path = c.fetchone()
                self.post_id = post_id
                self.date = date
                self.title = title
                self.body = body
                self.image_path = image_path
                self.image_name = None
                if image_path is not None:
                    try:
                        tmp = open(self.image_path,'rb')
                        self.image_data = tmp.read()
                    except IOError:
                        pass
                

    def save(self):
        if self.post_id is None:
            if self.image_name is not None:
                path = self.save_image(self.image_name,self.image_data)
                with connect_db() as conn:
                    conn.execute("""insert into Post 
                                    (date,title,body,image_path)
                                    VALUES
                                    (?,?,?,?)
                                    """,(self.date, self.title, self.body, path))
            else:
                with connect_db() as conn:
                    conn.execute("""insert into Post 
                                    (date,title,body)
                                    VALUES
                                    (?,?,?)
                                    """,(self.date, self.title, self.body))

                conn.commit()

    def save_image(self,filename,filedata):
        filename = secure_filename(filename)
        path = os.path.join(image_store,filename)
        logging.debug("dude come on: "+path)
        saveable = open(path,"wb")
        saveable.write(filedata)
        saveable.close()
        # save filtered copy
        murad_filter = filter.oldify
        the_file_object = open(path,"rb")
        # I think murad_filter takes a file object OR the path to a file
        image_object = murad_filter(the_file_object)

        filtered_path = os.path.join(filtered_image_store,filename)
        image_object.save(filtered_path)

        return path

    def show(self):
        with connect_db() as conn:
            c = conn.cursor()
            c.execute("select post_id,date,title,body from Post order by date")
            posts = [(i,d,t,b) for i,d,t,b in c]

        return posts

