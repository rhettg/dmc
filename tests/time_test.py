from testify import *
import datetime
import pytz

from dmc import (
    Time,
    TimeInterval,
    TimeSpan)


class InitTimeTestCase(TestCase):
    def test_direct(self):
        d = Time(2014, 4, 18, 17, 50, 21)

        assert_equal(d.year, 2014)
        assert_equal(d.month, 4)
        assert_equal(d.day, 18)
        assert_equal(d.hour, 17)
        assert_equal(d.minute, 50)
        assert_equal(d.second, 21)

    def test_direct_tz(self):
        d = Time(2014, 4, 18, 17, 50, 21, tz='America/Los_Angeles')

        assert_equal(d.year, 2014)
        assert_equal(d.month, 4)
        assert_equal(d.day, 19)
        assert_equal(d.hour, 1)
        assert_equal(d.minute, 50)
        assert_equal(d.second, 21)

    def test_direct_local(self):
        d = Time(2014, 4, 18, 17, 50, 21, local=True)

        assert_equal(d.year, 2014)
        assert_equal(d.month, 4)

        # can't really say for sure
        assert d.day in [18, 19]

        assert_equal(d.minute, 50)
        assert_equal(d.second, 21)

    def test_timestamp(self):
        ts = 1398125982.036391

        t = Time.from_timestamp(ts)

        assert_equal(t.year, 2014)
        assert_equal(t.month, 4)
        assert_equal(t.day, 22)
        assert_equal(t.hour, 0)
        assert_equal(t.minute, 19)
        assert_equal(t.second, 42)
        assert_equal(t.microsecond, 36391)

    def test_datetime_naive(self):
        dt = datetime.datetime(2014, 4, 18, 17, 50, 21)

        t = Time.from_datetime(dt)

        assert_equal(t.day, 18)
        assert_equal(t.hour, 17)
        assert_equal(t.minute, 50)
        assert_equal(t.second, 21)

    def test_datetime_tz(self):
        dt = datetime.datetime(2014, 4, 18, 17, 50, 21)
        dt = pytz.timezone('America/Los_Angeles').localize(dt)

        t = Time.from_datetime(dt)

        assert_equal(t.year, 2014)
        assert_equal(t.month, 4)
        assert_equal(t.day, 19)
        assert_equal(t.hour, 0)
        assert_equal(t.minute, 50)
        assert_equal(t.second, 21)

    def test_str(self):
        t = Time.from_str("2014-04-18T17:50:21.036391")

        assert_equal(t.year, 2014)
        assert_equal(t.month, 4)
        assert_equal(t.day, 18)
        assert_equal(t.hour, 17)
        assert_equal(t.minute, 50)
        assert_equal(t.second, 21)

    def test_str_tz(self):
        t = Time.from_str("2014-04-18T17:50:21.036391-07:00")

        assert_equal(t.year, 2014)
        assert_equal(t.month, 4)
        assert_equal(t.day, 19)
        assert_equal(t.hour, 0)
        assert_equal(t.minute, 50)
        assert_equal(t.second, 21)

    def test_str_specify_tz(self):
        t = Time.from_str("2014-04-18T17:50:21.036391", tz='America/Los_Angeles')

        assert_equal(t.year, 2014)
        assert_equal(t.month, 4)
        assert_equal(t.day, 19)
        assert_equal(t.hour, 0)
        assert_equal(t.minute, 50)
        assert_equal(t.second, 21)


class ConvertTimeTestCase(TestCase):
    @setup
    def create_time(self):
        self.t = Time(2014, 4, 18, 17, 50, 21, 36391)

    def test_str(self):
        assert_equal(self.t.to_str(), "2014-04-18T17:50:21.036391+00:00")

    def test_str_tz(self):
        assert_equal(self.t.to_str(tz='America/Los_Angeles'), "2014-04-18T10:50:21.036391-07:00")

    def test_str_local(self):
        # We don't really konw
        assert self.t.to_str(local=True)

    def test_str_format(self):
        assert_equal(self.t.to_str(format="%m/%d/%Y %H:%M"), "04/18/2014 17:50")

    def test_timestamp(self):
        assert_equal(self.t.to_timestamp(), 1397872221.036391)

    def test_datetime(self):
        dt = self.t.to_datetime()

        assert_equal(dt.year, 2014)
        assert_equal(dt.month, 4)
        assert_equal(dt.day, 18)
        assert_equal(dt.hour, 17)
        assert_equal(dt.minute, 50)
        assert_equal(dt.second, 21)
        assert_equal(dt.tzinfo, pytz.UTC)

    def test_datetime_tz(self):
        dt = self.t.to_datetime(tz='America/Los_Angeles')

        assert_equal(dt.year, 2014)
        assert_equal(dt.month, 4)
        assert_equal(dt.day, 18)
        assert_equal(dt.hour, 10)
        assert_equal(dt.minute, 50)
        assert_equal(dt.second, 21)
        assert_equal(str(dt.tzinfo), 'America/Los_Angeles')

    def test_datetime_local(self):
        dt = self.t.to_datetime(local=True)

        assert_equal(dt.year, 2014)
        assert_equal(dt.month, 4)

        assert_equal(dt.minute, 50)
        assert_equal(dt.second, 21)

    def test_human(self):
        # Just make sure it doesn't crash
        assert self.t.to_human()


class InitTimeIntervalTest(TestCase):
    def test_seconds(self):
        i = TimeInterval(21)

        assert_equal(i.seconds, 21)
        assert_equal(i.microseconds, 0)

    def test_float_seconds(self):
        i = TimeInterval(1.2)

        assert_equal(i.seconds, 1)
        assert_equal(i.microseconds, 200000)

    def test_minutes(self):
        i = TimeInterval(minutes=2)
        assert_equal(i.seconds, 120)
        assert_equal(i.microseconds, 0)

    def test_hours(self):
        i = TimeInterval(hours=1)
        assert_equal(i.seconds, 3600)
        assert_equal(i.microseconds, 0)

    def test_microseconds(self):
        i = TimeInterval(microseconds=10)
        assert_equal(i.seconds, 0)
        assert_equal(i.microseconds, 10)

    def test_microsecond_overflow(self):
        i = TimeInterval(seconds=1.9, microseconds=200000)
        assert_equal(i.seconds, 2)
        assert_equal(i.microseconds, 100000)


class ConvertTimeIntervalTest(TestCase):
    def test_int(self):
        i = TimeInterval(4)
        assert_equal(int(i), 4)

    def test_int_round(self):
        i = TimeInterval(4, microseconds=600000)
        assert_equal(int(i), 5)

    def test_float(self):
        i = TimeInterval(4, microseconds=600000)
        assert_equal(float(i), 4.6)

    def test_str(self):
        i = TimeInterval(hours=1, minutes=45, seconds=21, microseconds=600000)
        assert_equal(str(i), "+01:45:21.6")


class ArithmeticTimeIntervalTest(TestCase):
    def test_add(self):
        i1 = TimeInterval(1)
        i2 = TimeInterval(1)

        i3 = i1 + i2
        assert_equal(i3.seconds, 2)

    def test_add_int(self):
        i1 = TimeInterval(1)
        i2 = 1

        i3 = i1 + i2
        assert_equal(i3.seconds, 2)

        i4 = i2 + i1
        assert_equal(i4.seconds, 2)

    def test_sub(self):
        i1 = TimeInterval(2)
        i2 = TimeInterval(1)

        i3 = i1 - i2
        assert_equal(i3.seconds, 1)

    def test_sub_neg(self):
        i1 = TimeInterval(1)
        i2 = TimeInterval(2)

        i3 = i1 - i2
        assert_equal(i3.seconds, -1)

    def test_sub_int(self):
        i1 = TimeInterval(2)
        i2 = 1

        i3 = i1 - i2
        assert_equal(i3.seconds, 1)

        i4 = i2 - i1
        assert_equal(i4, -1)
