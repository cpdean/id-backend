import unittest
import db
import os, shutil
import datetime

os.environ['DATABASE_URL'] = "postgres://herokuflask@localhost/herokudb"

testenv = "testenv"

db.db = os.path.join(testenv, db.db)
db.image_store = os.path.join(testenv, db.image_store)

# refresh test environment
if os.path.exists(testenv):
  shutil.rmtree(testenv)
os.makedirs(testenv)

class TestDatabase(unittest.TestCase):
    
    def setUp(self):
        db.init_db()

    def injectSeveralPosts(self,n):
        for i in range(n):
            p = db.Post()
            p.title = "injected"
            p.save()


    def test_connect(self):
        c = db.connect_db()
        cur = c.cursor()
        # ensure the post table is there
        cur.execute("select exists(SELECT name FROM sqlite_master WHERE type='table' AND name=?);", ('post',))
        self.assertEqual(cur.fetchone()[0],True)

    def test_make_post(self):
        p = db.Post()
        p.title = "PostTitle"
        p.body = "Postbody"
        p.save()
        new_p = db.get_latest_post()

        self.assertEqual(new_p.title,p.title)
        self.assertEqual(new_p.body,p.body)

    def test_date_datatype(self):
        now = datetime.datetime.now()
        p = db.Post()
        p.date = now
        p.save()
        new_p = db.get_latest_post()

        self.assertEqual(new_p.date,p.date)

    def test_image_save(self):
        i_file = open("./test-data/black.jpg","rb")
        i_data = i_file.read()
        p = db.Post()
        p.title = "this is the image test"
        p.image_name = os.path.basename(i_file.name)
        p.image_data = i_data
        p.save()

        new_p = db.get_latest_post()
        original = p.image_data
        new = new_p.image_data

        self.assertEquals(original, new)

    def test_show_posts(self):
        self.injectSeveralPosts(10)
        posts = db.Post().show()
        self.assertEquals(len(posts),10)
        

if __name__ == '__main__':
    unittest.main()
