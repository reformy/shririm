from django.contrib.auth.models import User
from django.test import TestCase

from gym.models import Device


class TestPages(TestCase):
    """Every page renders (no missing templates)."""

    def setUp(self):
        self.user = User.objects.create_user(username='u', password='x')
        self.client.force_login(self.user)
        self.device = Device.objects.create(name='Bench', created_by=self.user)

    def test_pages(self):
        for url in ('/gym/', '/gym/devices/', '/gym/devices/create/', f'/gym/devices/{self.device.id}/edit/',
                    f'/gym/devices/{self.device.id}/delete/', '/gym/plans/', '/gym/plans/create/',
                    '/gym/sessions/', '/gym/sessions/start/', '/gym/profile/', '/gym/profile/edit/'):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_no_device_page(self):
        self.assertEqual(self.client.get(f'/gym/devices/{self.device.id}/').status_code, 404)

    def test_error_pages(self):
        """With DEBUG off, the site's own 404 and 500 pages are shown; they must render."""
        from django.test import RequestFactory
        from django.views.defaults import server_error
        response = server_error(RequestFactory().get('/'))
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Server Error', response.content)
        response = self.client.get('/no-such-page/')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Page Not Found', response.content)

    def test_errors_are_logged_not_shown(self):
        from unittest import mock
        with mock.patch('gym.views.Plan.objects.filter', side_effect=RuntimeError('secret internals')), \
                self.assertLogs('gym.views', 'ERROR') as logs:
            response = self.client.get('/gym/plans/')
        response = self.client.get(response.url)  # The page the error message is shown on.
        self.assertNotIn(b'secret internals', response.content)
        self.assertIn(b'An error occurred while loading plans. Please try again.', response.content)
        self.assertIn('secret internals', '\n'.join(logs.output))

    def test_logout_is_a_post(self):
        self.assertContains(self.client.get('/gym/'), 'action="/gym/accounts/logout/"')
        self.client.get('/gym/accounts/logout/')
        self.assertEqual(self.client.get('/gym/').status_code, 200)  # Still logged in.
        self.client.post('/gym/accounts/logout/')
        self.assertEqual(self.client.get('/gym/').status_code, 302)  # Logged out.
