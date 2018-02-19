"""
Authentication Unittests
"""
import datetime
import jwt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from tests import (F_REG_DATA, F_USER_DATA, FF_REG_DATA, FF_USER_DATA,
                   FFF_USER_DATA, REG_DATA, USER_DATA, app)
from tests.base import APITestCases, create_and_login_user, create_user


class AuthTestCases(APITestCases):
    """
    Test Cases for API Auth functionality
    """

    def test_user_can_register_successfully(self):
        """Test API can register a new user"""
        res0 = self.client.post('/auth/register', data=REG_DATA)
        self.assertEqual(res0.status_code, 201)

    def test_user_cant_register_with_wrong_password(self):
        res1 = self.client.post('/auth/register', data=F_REG_DATA)
        self.assertEqual(res1.status_code, 422)

    def test_user_cant_register_with_wrong_email(self):
        res2 = self.client.post('/auth/register', data=FF_REG_DATA)
        self.assertEqual(res2.status_code, 422)

    def test_login_fails_with_wrong_password(self):
        """Test API can login registered user"""
        create_user(self.client)
        res0 = self.client.post('/auth/login', data=F_USER_DATA)
        self.assertEqual(res0.status_code, 401)

    def test_login_fails_with_wrong_email(self):
        create_user(self.client)
        res1 = self.client.post('/auth/login', data=FF_USER_DATA)
        self.assertEqual(res1.status_code, 404)

    def test_login_fails_with_form_errors(self):
        create_user(self.client)
        res2 = self.client.post('/auth/login', data=FFF_USER_DATA)
        self.assertEqual(res2.status_code, 422)

    def test_successful_user_login(self):
        create_user(self.client)
        res3 = self.client.post('/auth/login', data=USER_DATA)
        self.assertEqual(res3.status_code, 200)

    def test_user_logout(self):
        """Test API can logout logged in user"""
        tkn = create_and_login_user(self.client)
        res1 = self.client.post(
            '/auth/logout',
            headers={
                'Content': 'application/x-www-form-urlencoded',
                'Authorization': tkn
            })
        self.assertEqual(res1.status_code, 200)

    def test_sending_resetlink_fails_given_form_errors(self):
        """
        Test API can send password reset link to email for forgotten passwords
        """
        create_and_login_user(self.client)
        res0 = self.client.post('/auth/forgot-password', data={'email': ''})
        self.assertEqual(res0.status_code, 422)
        res1 = self.client.post(
            '/auth/forgot-password', data={
                'email': 'test23@domain.com'
            })
        self.assertEqual(res1.status_code, 422)
        res2 = self.client.post(
            '/auth/forgot-password', data={
                'email': 'test@'
            })
        self.assertEqual(res2.status_code, 422)

    def test_password_resetlink_sent_successfully(self):
        create_and_login_user(self.client)
        res3 = self.client.post(
            '/auth/forgot-password', data={
                'email': USER_DATA['email']
            })
        self.assertEqual(res3.status_code, 200)

    def test_password_reset_fails_given_invalid_token(self):
        """Test API can reset forgotten password."""
        create_user(self.client)
        res1 = self.client.post('/auth/reset_password/daudi')
        self.assertEqual(res1.status_code, 401)

    def test_password_reset_fails_given_expired_token(self):
        create_user(self.client)
        try:
            payload = {
                'exp': datetime.datetime.utcnow()\
                        + datetime.timedelta(days=0, seconds=-30),
                'iat': datetime.datetime.utcnow(),
                'sub': 1
            }
            token = jwt.encode(
                payload, app.config.get('SECRET_KEY'), algorithm='HS256')
        except Exception as e:
            return e
        password_reset_url = "/auth/reset_password/" + token.decode()
        res2 = self.client.post(password_reset_url)
        self.assertEqual(res2.status_code, 401)

    def test_password_reset_fails_given_form_errors(self):
        create_user(self.client)
        try:
            payload = {
                'exp': datetime.datetime.utcnow()\
                        + datetime.timedelta(days=0, seconds=600),
                'iat': datetime.datetime.utcnow(),
                'sub': 1
            }
            token = jwt.encode(
                payload, app.config.get('SECRET_KEY'), algorithm='HS256')
        except Exception as e:
            return e
        password_reset_url = "/auth/reset_password/" + token.decode()
        res0 = self.client.post(
            password_reset_url, data={
                "new_password": 123,
                "confirm": 13
            })
        self.assertEqual(res0.status_code, 422)

    def test_successful_password_reset(self):
        create_user(self.client)
        try:
            payload = {
                'exp': datetime.datetime.utcnow()\
                        + datetime.timedelta(days=0, seconds=600),
                'iat': datetime.datetime.utcnow(),
                'sub': 1
            }
            token = jwt.encode(
                payload, app.config.get('SECRET_KEY'), algorithm='HS256')
        except Exception as e:
            return e
        password_reset_url = "/auth/reset_password/" + token.decode()
        res1 = self.client.post(
            password_reset_url, data={
                "new_password": 123,
                "confirm": 123
            })
        self.assertEqual(res1.status_code, 200)
