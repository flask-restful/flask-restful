import unittest
import datetime
from flask.ext.restful.fields import ISO8601Duration


class DatesTestCase(unittest.TestCase):
    def test_one_day_interval(self):
        d = ISO8601Duration("2010-11-12")
        self.assertEqual(d.value(), (datetime.datetime(2010, 11, 12), datetime.datetime(2010, 11, 13)))

    def test_days_interval(self):
        d = ISO8601Duration("2010-11-12/2010-11-15")
        self.assertEqual(d.value(), (datetime.datetime(2010, 11, 12), datetime.datetime(2010, 11, 15)))

    def test_date_duration(self):
        d = ISO8601Duration("2010-11-12/P1Y")
        self.assertEqual(d.value(), (datetime.datetime(2010, 11, 12), datetime.datetime(2011, 11, 12)))
        d = ISO8601Duration("2010-11-12/P1M")
        self.assertEqual(d.value(), (datetime.datetime(2010, 11, 12), datetime.datetime(2010, 12, 12)))
        d = ISO8601Duration("2010-11-12/P1M1D")
        self.assertEqual(d.value(), (datetime.datetime(2010, 11, 12), datetime.datetime(2010, 12, 13)))

    def test_duration_date(self):
        d = ISO8601Duration("P1Y/2013-10-12")
        self.assertEqual(d.value(), (datetime.datetime(2012, 10, 12), datetime.datetime(2013, 10, 12)))

    def test_precise_interval(self):
        d = ISO8601Duration("2010-11-12T01:02:03/2010-11-12T04:05:06")
        self.assertEqual(d.value(), (datetime.datetime(2010, 11, 12, 1, 2, 3), datetime.datetime(2010, 11, 12, 4, 5, 6)))

    def test_microsecond_interval(self):
        d = ISO8601Duration("2010-11-12T01:02:03.234567/2010-11-12T04:05:06")
        self.assertEqual(d.value(), (datetime.datetime(2010, 11, 12, 1, 2, 3, 234567), datetime.datetime(2010, 11, 12, 4, 5, 6)))

    def test_microsecond_duration(self):
        d = ISO8601Duration("2010-11-12T01:02:03.234567/PT0.000001S")
        self.assertEqual(d.value(), (datetime.datetime(2010, 11, 12, 1, 2, 3, 234567), datetime.datetime(2010, 11, 12, 1, 2, 3, 234568)))

    def test_openended_right(self):
        d = ISO8601Duration("2010-11-12T01:02:03.234567/")
        self.assertEqual(d.value(), (datetime.datetime(2010, 11, 12, 1, 2, 3, 234567), datetime.datetime(datetime.MAXYEAR, 12, 31)))

    def test_openended_left(self):
        d = ISO8601Duration("/2010-11-12T01:02:03.234567")
        self.assertEqual(d.value(), (datetime.datetime(datetime.MINYEAR, 1, 1), datetime.datetime(2010, 11, 12, 1, 2, 3, 234567)))

if __name__ == '__main__':
    unittest.main()
