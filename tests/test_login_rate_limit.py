from unittest import mock

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import Client, TestCase

from gym import login_rate_limit


class TestLoginRateLimit(TestCase):
    def setUp(self):
        User.objects.create_user(username='u', password='a-password-1', is_staff=True)
        cache.clear()
        self.addCleanup(cache.clear)
        patcher = mock.patch.object(login_rate_limit, 'FAILED_RATE', '3/h')
        patcher.start()
        self.addCleanup(patcher.stop)

    @staticmethod
    def _login(url, password, ip='10.0.0.1'):
        return Client(HTTP_X_REAL_IP=ip).post(url, {'username': 'u', 'password': password})

    def test_blocked_after_failures(self):
        for url in ('/gym/accounts/login/', '/admin/login/'):
            with self.subTest(url=url):
                cache.clear()
                for _ in range(3):
                    self.assertEqual(self._login(url, 'wrong').status_code, 200)
                response = self._login(url, 'a-password-1')
                self.assertEqual(response.status_code, 429)
                self.assertIn(b'Try again in ', response.content)

    def test_successful_logins_dont_count(self):
        for _ in range(5):
            self.assertEqual(self._login('/gym/accounts/login/', 'a-password-1').status_code, 302)

    def test_other_ips_not_blocked(self):
        for _ in range(4):
            self._login('/gym/accounts/login/', 'wrong')
        self.assertEqual(self._login('/gym/accounts/login/', 'a-password-1', ip='10.0.0.2').status_code, 302)

    def test_real_ip_header(self):
        """The limit is per X-Real-IP (the client, on PythonAnywhere), not per REMOTE_ADDR (its balancer)."""
        for _ in range(3):
            Client(HTTP_X_REAL_IP='10.0.0.1', REMOTE_ADDR='192.168.0.1').post(
                '/gym/accounts/login/', {'username': 'u', 'password': 'wrong'})
        response = Client(HTTP_X_REAL_IP='10.0.0.3', REMOTE_ADDR='192.168.0.1').post(
            '/gym/accounts/login/', {'username': 'u', 'password': 'a-password-1'})
        self.assertEqual(response.status_code, 302)
