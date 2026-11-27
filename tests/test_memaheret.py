import json
import os
import tempfile
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase

from shririm.memaheret import view

GOOD = 'שלומי'  # Five different letters.


class MemaheretTestCase(TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        patcher = mock.patch.object(view, '__location__', self.dir.name)
        patcher.start()
        self.addCleanup(patcher.stop)
        self._write('new_words.txt', [GOOD])
        self._write('no_words.txt', [])

    def _write(self, name, words):
        with open(os.path.join(self.dir.name, name), 'w') as f:
            f.writelines(w + '\n' for w in words)

    def _read(self, name):
        with open(os.path.join(self.dir.name, name)) as f:
            return [w.strip() for w in f]


class TestWordOfTheDay(MemaheretTestCase):
    def test_word(self):
        body = self.client.get('/woth.js').content.decode()
        self.assertTrue(body.startswith('const word_of_the_day = ') and body.endswith(';'))
        self.assertEqual(json.loads(body[len('const word_of_the_day = '):-1]), GOOD)

    def test_injected_lines_are_not_served(self):
        self._write('new_words.txt', [GOOD, '"; alert(1); "', 'abcde'])
        for _ in range(20):
            self.assertNotIn('alert', self.client.get('/woth.js').content.decode())


class TestAddWords(MemaheretTestCase):
    URL = '/add_word/'

    def _login(self, superuser):
        make = User.objects.create_superuser if superuser else User.objects.create_user
        self.client.force_login(make(username='u', password='x'))

    def test_logged_out(self):
        response = self.client.post(self.URL, {'word': GOOD, 'good': 'Good', 'words': ''})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/gym/accounts/login/', response.url)
        self.assertEqual(self._read('new_words.txt'), [GOOD])

    def test_not_superuser(self):
        self._login(superuser=False)
        self.assertEqual(self.client.get(self.URL).status_code, 403)
        self.assertEqual(self.client.post(self.URL, {'word': 'אבגדה', 'good': 'Good', 'words': ''}).status_code, 403)

    def test_superuser_adds_words(self):
        self._login(superuser=True)
        response = self.client.post(self.URL, {'word': 'אבגדה', 'good': 'Good', 'words': 'הזחטי\nbad\nאאאאא'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self._read('new_words.txt'), [GOOD, 'אבגדה', 'הזחטי'])

    def test_bad_word_is_not_written(self):
        self._login(superuser=True)
        self.client.post(self.URL, {'word': '"; alert(1); "', 'good': 'Good', 'words': ''})
        self.client.post(self.URL, {'word': 'אבגדה\nאבגדה', 'good': 'Good', 'words': ''})
        self.assertEqual(self._read('new_words.txt'), [GOOD])

    def test_page(self):
        self._login(superuser=True)
        with mock.patch.object(view, 'FREQUENT_WORDS', ['אבגדה']):
            self.assertContains(self.client.get(self.URL), 'אבגדה')


class TestLoginNext(TestCase):
    URL = '/gym/accounts/login/'

    def setUp(self):
        User.objects.create_user(username='u', password='a-password-1')

    def _login(self, next_url):
        return self.client.post(f'{self.URL}?next={next_url}', {'username': 'u', 'password': 'a-password-1'})

    def test_next_on_this_site(self):
        self.assertEqual(self._login('/add_word/').url, '/add_word/')

    def test_next_elsewhere_is_ignored(self):
        self.assertEqual(self._login('https://evil.example/').url, '/gym/')

    def test_no_next(self):
        self.assertEqual(self.client.post(self.URL, {'username': 'u', 'password': 'a-password-1'}).url, '/gym/')
