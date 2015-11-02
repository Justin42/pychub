import unittest
from mongoengine import connect
from pychub.model.User import User
from pychub.view import auth
from pyramid import testing


class ViewsTest(unittest.TestCase):
    def setUp(self):
        self.db = connect('Test')
        self.config = testing.setUp()
        User.drop_collection()

    def tearDown(self):
        self.db.disconnect()

    def test_auth_login(self):
        request = testing.DummyRequest()
        request.params = {'username': 'TestUser', 'password': 'test'}
        response = auth.login(request)
        self.assertEqual(response['message'], 'Login failed.')
        self.assertEqual(response['username'], 'TestUser')
        user = User()
        user.username = 'TestUser'
        user.email = 'test@example.com'
        user.set_password('test')
        user.save()
        response = auth.login(request)
        self.assertEqual(response['message'], 'Success')
        self.assertEqual(response['username'], 'TestUser')