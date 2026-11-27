from datetime import datetime, timezone

from django.test import SimpleTestCase

from gym.templatetags import timezone_filters as f


class TestTimezoneFilters(SimpleTestCase):
    """Times given without a time zone are taken as UTC (django.utils.timezone.utc is gone since Django 5)."""
    NAIVE = datetime(2026, 11, 27, 3, 0)
    AWARE = datetime(2026, 11, 27, 3, 0, tzinfo=timezone.utc)

    def test_in_user_timezone(self):
        for value in (self.NAIVE, self.AWARE):
            local = f.in_user_timezone(value, 'Australia/Melbourne')
            self.assertEqual((local.hour, local.utcoffset().total_seconds() / 3600), (14, 11))

    def test_tags(self):
        for tag in (f.format_datetime_in_timezone, f.format_date_in_timezone, f.format_time_in_timezone):
            with self.subTest(tag=tag.__name__):
                self.assertEqual(tag(self.NAIVE, 'Australia/Melbourne'), tag(self.AWARE, 'Australia/Melbourne'))
