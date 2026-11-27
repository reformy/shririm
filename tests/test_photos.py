import io
import os
import tempfile
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase, override_settings
from PIL import Image, UnidentifiedImageError

from gym.forms import DeviceForm
from gym.models import Device
from gym.photos import PhotoField, open_photo


def _image(fmt: str, mode: str = 'RGB') -> bytes:
    b = io.BytesIO()
    Image.new(mode, (20, 10), 'red').save(b, fmt)
    return b.getvalue()


def _form(name, data):
    return DeviceForm({'name': 'Bench'}, {'image': SimpleUploadedFile(name, data)})


class TestOpenPhoto(SimpleTestCase):
    def test_photo_formats(self):
        for fmt in ('JPEG', 'PNG', 'WEBP'):
            self.assertEqual(open_photo(io.BytesIO(_image(fmt))).format, fmt)

    def test_other_formats(self):
        for fmt in ('TIFF', 'BMP', 'GIF', 'PCX'):
            with self.assertRaises(UnidentifiedImageError):
                open_photo(io.BytesIO(_image(fmt)))

    def test_too_many_pixels(self):
        with mock.patch.object(Image, 'MAX_IMAGE_PIXELS', 199):  # The image is 200; Pillow only warns up to twice.
            with self.assertRaises(Image.DecompressionBombError):
                open_photo(io.BytesIO(_image('PNG')))


class TestDeviceForm(SimpleTestCase):
    def test_photos(self):
        for fmt, name in (('JPEG', 'a.jpg'), ('PNG', 'a.png'), ('WEBP', 'a.webp')):
            self.assertTrue(_form(name, _image(fmt)).is_valid(), name)

    def test_no_image(self):
        self.assertTrue(DeviceForm({'name': 'Bench'}).is_valid())

    def test_not_photos(self):
        for fmt, name in (('TIFF', 'a.tiff'), ('TIFF', 'a.jpg'), ('GIF', 'a.png'), ('JPEG', 'a.tif')):
            self.assertFalse(_form(name, _image(fmt)).is_valid(), (fmt, name))

    def test_too_big(self):
        with mock.patch.object(PhotoField, 'MAX_BYTES', 100):
            form = _form('a.png', _image('PNG') + b'\0' * 100)
            self.assertFalse(form.is_valid())
            self.assertIn('too big', str(form.errors))

    def test_accept(self):
        self.assertIn('accept="image/jpeg,image/png,image/webp"', str(DeviceForm()['image']))


class TestDeviceCreate(TestCase):
    def test_photo_is_saved(self):
        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            user = User.objects.create_user(username='u', password='x')
            self.client.force_login(user)
            response = self.client.post('/gym/devices/create/', {
                'name': 'Bench', 'description': '', 'image': SimpleUploadedFile('bench.png', _image('PNG'))})
            self.assertEqual(response.status_code, 302)
            device = Device.objects.get(created_by=user)
            self.assertTrue(device.image.name.startswith('device_images/bench'))
            self.assertTrue(os.path.exists(device.image.path))
