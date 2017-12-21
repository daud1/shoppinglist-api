"""
Authentication Unittests
"""
from tests import (APP, F_REG_DATA, F_USER_DATA, FF_REG_DATA, FF_USER_DATA,
                   FFF_USER_DATA, REG_DATA, USER_DATA, APITestCases,
                   Serializer, create_and_login_user)


class AuthTestCases(APITestCases):
    """
    Test Cases for API Auth functionality
    """
    def test_user_register(self):
        """Test API can register a new user"""
        with APP.test_client() as client:
            res0 = client.post('/auth/register', data=REG_DATA)
            self.assertEqual(res0.status_code, 201)
            res1 = client.post('/auth/register', data=F_REG_DATA)
            self.assertEqual(res1.status_code, 422)
            res2 = client.post('/auth/register', data=FF_REG_DATA)
            self.assertEqual(res2.status_code, 422)

    def test_user_login(self):
        """Test API can login registered user"""
        with APP.test_client() as client:
            client.post('/auth/register', data=REG_DATA)
            res0 = client.post('/auth/login', data=F_USER_DATA)
            self.assertEqual(res0.status_code, 401)
            res1 = client.post('/auth/login', data=FF_USER_DATA)
            self.assertEqual(res1.status_code, 404)
            res2 = client.post('/auth/login', data=FFF_USER_DATA)
            self.assertEqual(res2.status_code, 422)
            res3 = client.post('/auth/login', data=USER_DATA)
            self.assertEqual(res3.status_code, 200)

    def test_user_logout(self):
        """Test API can logout logged in user"""
        with APP.test_client() as client:
            tkn = create_and_login_user(client)
            res1 = client.post('/auth/logout',
                               headers={
                                   'Content':          'Application/x-www-form-urlencoded',
                                   'Authorization':    'Basic %s' % tkn
                               })
            self.assertEqual(res1.status_code, 200)

    def test_password_forgotten_route(self):
        """
        Test API can send password reset link to email for forgotten passwords
        """
        with APP.test_client() as client:
            create_and_login_user(client)
            res0 = client.post('/auth/forgot-password',
                               data={'email': ''})
            self.assertEqual(res0.status_code, 422)
            res1 = client.post('/auth/forgot-password',
                               data={'email': 'test23@domain.com'})
            self.assertEqual(res1.status_code, 422)
            res2 = client.post('/auth/forgot-password',
                               data={'email': 'test@'})
            self.assertEqual(res2.status_code, 422)
            # res3 = client.post('/auth/forgot-password',
            #                    data={'email': USER_DATA['email']})
            # self.assertEqual(res3.status_code, 200)

    def test_password_reset_route(self):
        """Test API can reset forgotten password."""
        with APP.test_client() as client:
            client.post('/auth/register', data=REG_DATA)
            res1 = client.post('/auth/reset_password/daudi')
            self.assertEqual(res1.status_code, 401)
            
            ser = Serializer(APP.config['SECRET_KEY'], expires_in=-60)
            token = ser.dumps({'email': 'test@domain.com'})
            password_reset_url = "/auth/reset_password/" + token.decode("utf-8")
            res2 = client.post(password_reset_url)
            self.assertEqual(res2.status_code, 401)

            ser = Serializer(APP.config['SECRET_KEY'], expires_in=360)
            token = ser.dumps({'email': 'test@domain.com'})
            password_reset_url = "/auth/reset_password/" + token.decode("utf-8")
            res0 = client.post(password_reset_url, data={"new_password": 123, "confirm": 13})
            self.assertEqual(res0.status_code, 422)

            ser = Serializer(APP.config['SECRET_KEY'], expires_in=360)
            token = ser.dumps({'email': 'test@domain.com'})
            password_reset_url = "/auth/reset_password/" + token.decode("utf-8")
            res1 = client.post(password_reset_url, data={"new_password": 123, "confirm": 123})
            self.assertEqual(res1.status_code, 200)