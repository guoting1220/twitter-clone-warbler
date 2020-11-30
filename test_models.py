""" models tests."""

# run these tests like:
#    python -m unittest test_models.py

import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class ModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Likes.query.delete()

        # self.client = app.test_client()
  

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )      

        db.session.add(u)
        db.session.commit()

        u_id = u.id

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.following), 0)
        self.assertEqual(len(u.likes), 0)
        self.assertIn(u.__repr__(), f"<User #{u_id}: testuser, test@test.com>")

        # test valid sign up
        signed_user = User.signup(
            "test", "email@email.com", "password", None)

        db.session.commit()

        self.assertTrue(signed_user, 0)

        test_user = User.query.get(signed_user.id)
        self.assertEqual(test_user.username, "test")
        self.assertEqual(test_user.email, "email@email.com")
        self.assertNotEqual(test_user.password, "password")
        self.assertEqual(test_user.image_url, "/static/images/default-pic.png")
      

        # test invalid username sign up (referencing the solution)
        invalid_1 = User.signup(None, "test@test.com", "password", None)
        uid = 123456789
        invalid_1.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
        db.session.rollback()


        # test invalid email sign up (referencing the solution)
        invalid_2 = User.signup("testtest", None, "password", None)
        uid = 123789
        invalid_2.id = uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()       
        db.session.rollback()

        # with self.assertRaises(exc.IntegrityError) as context:
        #     User.signup("test2", None, "password", None)


        # test invalid password sign up (referencing the solution)
        with self.assertRaises(ValueError) as context:
            User.signup("test3", "email@email.com", "", None)

        with self.assertRaises(ValueError) as context:
            User.signup("test4", "email@email.com", None, None)

        
        # test valid authentication
        self.assertEqual(
            User.authenticate("test", "password"), signed_user
        )

        # test invalid authentication
        self.assertEqual(
            User.authenticate("test", "sss"), False
        )

        self.assertEqual(
            User.authenticate("XXX", "password"), False
        )

    def test_follows_model(self):
        """test the Follows model"""

        u1 = User.signup("test1", "email1@email.com", "password", None)

        u2 = User.signup("test2", "email2@email.com", "password", None)

        db.session.commit()

        u1_id = u1.id
        u2_id = u2.id

        follow1 = Follows(
            user_being_followed_id=u1_id, user_following_id=u2_id
        )

        db.session.add(follow1)
        db.session.commit()

        self.assertEqual(len(u1.followers), 1)
        self.assertEqual(u1.followers[0], u2)
        self.assertEqual(len(u1.following), 0)
        self.assertEqual(len(u2.following), 1)
        self.assertEqual(u2.following[0], u1)
        self.assertEqual(len(u2.followers), 0)

        # test function is_followed_by
        self.assertEqual(u1.is_followed_by(u2), True)
        self.assertEqual(u2.is_following(u1), True)


    def test_message_model(self):
        """test the Message model"""

        u1 = User.signup("test1", "email1@email.com", "password", None)

        u2 = User.signup("test2", "email2@email.com", "password", None)

        db.session.commit()

        u1_id = u1.id
        u2_id = u2.id

        msg1 = Message(
            text="msgtext", 
            timestamp=None, 
            user_id=u1_id
        )

        db.session.add(msg1)
        db.session.commit()

        msg1_id = msg1.id

        self.assertEqual(msg1.user, u1)
        self.assertEqual(len(u1.messages), 1)
        self.assertEqual(u1.messages[0].text, "msgtext")

        # test Likes model
        like = Likes(user_id=u2_id, message_id=msg1_id)

        db.session.add(like)
        db.session.commit()

        self.assertEqual(len(u2.likes), 1)
        self.assertEqual(u2.likes[0], msg1)

        # test function is_liked_by for User model
        self.assertEqual(msg1.is_liked_by(u2), True)
    
  



