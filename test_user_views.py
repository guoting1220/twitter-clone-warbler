"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase
from models import db, connect_db, Message, User, Likes, Follows
# from bs4 import BeautifulSoup

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self): 
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()


    def test_list_users(self):
        """ test showing the users list """

        u = User.signup("other", "email1@email.com",
                        "password", None)
       
        db.session.commit()

        with self.client as c:
            resp = c.get("/users")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("other", html)
            self.assertIn("testuser", html)


    def test_show_user(self):
        """ test showing the user by id """

        u = User.signup("other", "email1@email.com", "password", None)

        db.session.commit()

        with self.client as c:
            resp = c.get(f"/users/{u.id}")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("other", html)
            self.assertNotIn("testuser", html)


    def test_show_following(self):
        """ test showing the followings of a user """

        u = User.signup("other", "email1@email.com", "password", None)

        db.session.commit()

        u_id = u.id

        follow = Follows(
            user_being_followed_id=u.id, user_following_id=self.testuser.id
                )

        db.session.add(follow)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}/following")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("other", html)   
            self.assertIn("Unfollow", html)

       
            # with c.session_transaction() as sess:
            #     sess[CURR_USER_KEY] = u_id

            # resp = c.get(f"/users/{self.testuser.id}/following")
            # html = resp.get_data(as_text=True)
            # self.assertEqual(resp.status_code, 200)
            # self.assertIn("What's Happening", html)

   

    def test_unauthorized_following_page_access(self):
        with self.client as c:
            resp = c.get(
                f"/users/{self.testuser.id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            # self.assertNotIn("@abc", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))


    def test_show_follower(self):
        """ test showing the followers of a user """

        u = User.signup("other", "email1@email.com", "password", None)

        db.session.commit()

        follow = Follows(
            user_being_followed_id=self.testuser.id, user_following_id=u.id
            )

        db.session.add(follow)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}/followers")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("other", html)      


    def test_unauthorized_followers_page_access(self):
        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            # self.assertNotIn("@abc", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))


    def test_add_follow(self):
        """ test add a follow for the logged-in user """

        u = User.signup("other", "email1@email.com", "password", None)

        db.session.commit()

        testuser_id = self.testuser.id

        # comment this line will ewsult in error ?? why
        u_id = u.id

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/users/follow/{u.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("other", html)
            self.assertIn("Unfollow", html)

            # follows = Follows.query.filter(
            #     Follows.user_following_id == testuser_id).all()
            # self.assertEqual(len(follows), 1)
            # self.assertEqual(
            #     follows[0].user_being_followed_id, u.id)


    def test_remove_follow(self):
        """ test remove a follow for the logged-in user """

        u = User.signup("other", "email1@email.com", "password", None)

        db.session.commit()

        follow = Follows(
            user_being_followed_id=u.id, user_following_id=self.testuser.id
            )

        db.session.add(follow)
        db.session.commit()        

        # comment this line will ewsult in error ?? why
        u_id = u.id

        with self.client as c:
            with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/users/stop-following/{u.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("other", html)
            

    def test_show_likes(self):
        """ test show a user's likes """

        u = User.signup("other", "email1@email.com", "password", None)

        db.session.commit()

        m = Message(text="The earth is round",
                    user_id=u.id)
        db.session.add(m)
        db.session.commit()

        like = Likes(user_id=self.testuser.id, message_id=m.id)       

        # why must have thish line, but m_id never been used
        m_id = m.id

        with self.client as c:
            with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}/likes")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("other", html)
            

    def test_add_like(self):

        u = User.signup("other", "email1@email.com", "password", None)

        db.session.commit()

        m = Message(text="The earth is round",
                    user_id=u.id)                   

        db.session.add(m)
        db.session.commit()

        # why must have thish line, but m_id never been used
        m_id = m.id

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/messages/{m.id}/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # why below cannot be: == m.id 
            likes = Likes.query.filter(Likes.message_id == m.id).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.testuser.id)
            

    def test_update_profile(self):
        """ test update user's profile """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get('/users/profile')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit Your Profile", html)

            resp = c.post('/users/profile')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit Your Profile", html)



