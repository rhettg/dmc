from testify import *
import datetime
import pytz

from dmc import (
    Time,
    Date,
    DateInterval,
    MockNow)


class InitDateTestCase(TestCase):
    def test_direct(self):
        d = Date(2014, 4, 18)

        assert_equal(d.year, 2014)
        assert_equal(d.month, 4)
        assert_equal(d.day, 18)


class ConvertDateTestCase(TestCase):
    def test_human(self):
        d = Date(2014, 4, 18)

        # This might fail under different locale?
        assert_equal(d.to_human(), "Apr 18")

    def test_human_tz(self):
        t = Time(2014, 4, 18, 0, 0, 0)

        d = Date(2014, 4, 18)
        with MockNow(t):
            assert_equal(d.to_human(), 'today')
            assert_equal(d.to_human(tz='America/Los_Angeles'), 'tomorrow')
