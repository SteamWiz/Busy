
import unittest
from datetime import date as Date
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

import busy.util.date_util


class TestDate(TestCase):

    @mock.patch('busy.util.date_util.today', lambda: Date(2019, 2, 11))
    def test_today(self):
        t = busy.util.date_util.relative_date('today')
        self.assertEqual(t, Date(2019, 2, 11))

    @mock.patch('busy.util.date_util.today', lambda: Date(2024, 11, 22))
    def test_monday(self):
        t = busy.util.date_util.relative_date('mon')
        self.assertEqual(t, Date(2024, 11, 25))

    @mock.patch('busy.util.date_util.today', lambda: Date(2024, 11, 22))
    def test_day_of_month(self):
        t = busy.util.date_util.relative_date('4')
        self.assertEqual(t, Date(2024, 12, 4))

    @mock.patch('busy.util.date_util.today', lambda: Date(2024, 11, 22))
    def test_day_of_month_same_day(self):
        t = busy.util.date_util.relative_date('27')
        self.assertEqual(t, Date(2024, 11, 27))

    @mock.patch('busy.util.date_util.today', lambda: Date(2024, 11, 22))
    def test_month_and_day(self):
        t = busy.util.date_util.relative_date('2-4')
        self.assertEqual(t, Date(2025, 2, 4))

    @mock.patch('busy.util.date_util.today', lambda: Date(2024, 11, 22))
    def test_month_and_day_same_year(self):
        t = busy.util.date_util.relative_date('12-4')
        self.assertEqual(t, Date(2024, 12, 4))
