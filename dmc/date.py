from __future__ import absolute_import

# -*- coding: utf-8 -*-

"""
This module contains the set of dmcs's exceptions

:copyright: (c) 2014 by Rhett Garber.
:license: ISC, see LICENSE for more details.

"""
import datetime

from . import human
from .time import Time


class Date(object):
    def __init__(self, year, month, day):
        self._d = datetime.date(year, month, day)

    @classmethod
    def from_datetime_date(cls, d):
        return Date(d.year, d.month, d.day)

    @classmethod
    def from_time(cls, t, tz=None, local=False):
        dt = t.to_datetime(tz=tz, local=local)
        return Date(dt.year, dt.month, dt.day)

    @classmethod
    def now(cls, t, tz=None, local=False):
        t = Time.now()
        return cls.from_time(t, tz=tz, local=local)

    @property
    def year(self):
        return self._d.year

    @property
    def month(self):
        return self._d.month

    @property
    def day(self):
        return self._d.day

    def to_str(self, format=None, tz=None, local=False):
        if format:
            return self._d.strftime(format)
        else:
            return self._d.isoformat()

    def to_human(self, tz=None, local=False):
        # We need to allow for timezone here because things like 'yesterday'
        # are highly dependent on what time it is locally.
        return human.naturaldate(self._d, tz=tz, local=local)

    def to_datetime_date(self):
        return self._d

    def __cmp__(self, other):
        raise NotImplemented

    def __add__(self, other):
        raise NotImplemented

    def __sub__(self, other):
        raise NotImplemented


class DateInterval(object):
    pass


class DateSpan(object):
    pass


class DateIterator(object):
    pass


class DateSpanIterator(object):
    pass
