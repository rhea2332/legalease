# social/tests.py
from django.test import TestCase
from django.contrib import auth

from social.models import User, Profile, Message

TEST_USERNAME = 'testuser'
TEST_PASSWORD = 'password123'

class UserTestCase(TestCase):

    def setUp(self):
        testuser = User.objects.create(username=TEST_USERNAME)
        testuser.set_password(TEST_PASSWORD)
        # need to save after setting password
        testuser.save()
    
    def test_user_exists(self):
        """Check if the test user exists"""
        
        testuser = User.objects.get(username=TEST_USERNAME)
        self.assertIsNotNone(testuser)

    def test_users_count(self):
        """Check that we have 1 user in test DB"""

        n_users = User.objects.all().count()
        self.assertEqual(n_users, 1)

    def test_testuser_password_set(self):
        """Check that password for user testuser has been set"""

        user = auth.authenticate(username=TEST_USERNAME, password=TEST_PASSWORD)
        self.assertIsNotNone(user)
        
    def test_testuser_password_match(self):
        """Check testuser password is matching in the DB."""
        
        self.assertTrue(auth.authenticate(username=TEST_USERNAME, password=TEST_PASSWORD))
        
TEST_TEXT = "This is a sample text"
TEST_TEXT2 = "This is a sample text2"

class ProfileTestCase(TestCase):
    
    def setUp(self):
        Profile.objects.create(text=TEST_TEXT)
        Profile.objects.create(text=TEST_TEXT2)
    
    def test_profile_exists(self):
        """Check Profile Exists"""
        
        self.assertIsNotNone(Profile.objects.get(text=TEST_TEXT2))
        self.assertIsNotNone(Profile.objects.get(text=TEST_TEXT))
        
    def test_profile_count(self):
        """Check Profile Count is 2"""
        
        profile_count = Profile.objects.count()
        self.assertEqual(profile_count, 2)
    
    def test_profile_text(self):
        """Check Profile Text matches the entry"""
        
        profile1 = Profile.objects.get(text=TEST_TEXT)
        profile2 = Profile.objects.get(text=TEST_TEXT2)
        
        self.assertIsNotNone(profile1)
        self.assertIsNotNone(profile2)

TEST_USERNAME2 = 'testuser2'

class MessageTestCase(TestCase):
    
    def setUp(self):
        test_sender = User.objects.create(username=TEST_USERNAME)
        test_sender.set_password(TEST_PASSWORD)
        test_sender.save()
        test_recip = User.objects.create(username=TEST_USERNAME2)
        test_recip.set_password(TEST_PASSWORD)
        test_recip.save()
        
        Message.objects.create(
                               sender=test_sender,
                               recip=test_recip,
                               text=TEST_TEXT,
                               public=True
                            )
        
    def test_message_exists(self):
        """Checks if Message Created Exists in the DB"""
        
        test_sender = User.objects.get(username=TEST_USERNAME)
        test_recip = User.objects.get(username=TEST_USERNAME2)
        
        message = Message.objects.get(sender=test_sender, recip=test_recip)
        self.assertIsNotNone(message)

    def test_message_count(self):
        """Checks if Message count is 1"""
        
        count = Message.objects.count()
        self.assertEqual(count, 1)
        
    def test_text_validation(self):
        """Checks if the text matches, with the value, fed to the DB"""
        
        test_sender = User.objects.get(username=TEST_USERNAME)
        test_recip = User.objects.get(username=TEST_USERNAME2)
        
        message = Message.objects.get(sender=test_sender, recip=test_recip)
        self.assertEqual(message.text, TEST_TEXT)
        
    def test_public_validation(self):
        """Checks if the Public Flag matches, with the value, fed to the DB"""
        
        test_sender = User.objects.get(username=TEST_USERNAME)
        test_recip = User.objects.get(username=TEST_USERNAME2)
        
        message = Message.objects.get(sender=test_sender, recip=test_recip)
        self.assertTrue(message.public)
        
    def test_sender_recip(self):
        """Checks if recip and sender matches the desired set value in DB"""
        
        test_sender = User.objects.get(username=TEST_USERNAME)
        test_recip = User.objects.get(username=TEST_USERNAME2)
        
        message = Message.objects.get(sender=test_sender, recip=test_recip)
        self.assertEqual(message.recip, test_recip)
        self.assertEqual(message.sender, test_sender)