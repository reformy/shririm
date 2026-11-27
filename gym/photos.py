"""
Device photos people upload are read as JPEG, PNG or WebP only. Pillow can read many more formats, and most
of its security bugs are in those (TIFF, EPS through Ghostscript, PDF, ...), so they stay off.
"""
from io import BytesIO

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from PIL import Image

PHOTO_FORMATS = ('JPEG', 'PNG', 'WEBP')
PHOTO_EXTENSIONS = ('jpg', 'jpeg', 'png', 'webp')


def open_photo(fp) -> Image.Image:
    """
    Image.open, for the photo formats only (others raise PIL.UnidentifiedImageError), and for at most
    Image.MAX_IMAGE_PIXELS (about 89 million, more than phone cameras take): Pillow itself only warns up to twice
    that, and decoding such a "decompression bomb" takes all the memory. Raises Image.DecompressionBombError.
    """
    image = Image.open(fp, formats=PHOTO_FORMATS)
    if Image.MAX_IMAGE_PIXELS and image.width * image.height > Image.MAX_IMAGE_PIXELS:
        image.close()
        raise Image.DecompressionBombError(f'The image is too big: {image.width} x {image.height} pixels.')
    return image


class PhotoField(forms.ImageField):
    """An ImageField for JPEG, PNG and WebP only, up to MAX_BYTES."""
    MAX_BYTES = 25 * 1024 * 1024
    default_validators = [FileExtensionValidator(PHOTO_EXTENSIONS)]

    def to_python(self, data):
        # Like Django 5.2's ImageField.to_python, with open_photo instead of Image.open (re-check it when upgrading
        # Django). Calling super() would open the file with all of Pillow's formats.
        f = forms.FileField.to_python(self, data)
        if f is None:
            return None
        if f.size > self.MAX_BYTES:
            raise ValidationError(f'The image is too big (at most {self.MAX_BYTES // (1024 * 1024)} MB).',
                                  code='too_big')
        if hasattr(data, 'temporary_file_path'):
            file = data.temporary_file_path()
        elif hasattr(data, 'read'):
            file = BytesIO(data.read())
        else:
            file = BytesIO(data['content'])
        try:
            image = open_photo(file)
            image.verify()
            f.image = image
            f.content_type = Image.MIME.get(image.format)
        except Exception as exc:
            raise ValidationError(self.error_messages['invalid_image'], code='invalid_image') from exc
        if hasattr(f, 'seek') and callable(f.seek):
            f.seek(0)
        return f

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if attrs.get('accept') == 'image/*':
            attrs['accept'] = 'image/jpeg,image/png,image/webp'
        return attrs
