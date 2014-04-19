from testify import *

from dmc import Time


class InitTestCase(TestCase):
    def test_direct(self):
        d = Time(2014, 4, 18, 17, 50, 21)

        assert_equal(d.year, 2014)
        assert_equal(d.month, 4)
        assert_equal(d.day, 18)
        assert_equal(d.hour, 17)
        assert_equal(d.minute, 50)
        assert_equal(d.second, 21)

    def test_direct_tz(self):
        pass

    def test_direct_local(self):
        pass
