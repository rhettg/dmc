# -*- coding: utf-8 -*-

"""
This module contains the set of dmcs's exceptions

:copyright: (c) 2014 by Rhett Garber.
:license: ISC, see LICENSE for more details.

"""
import datetime
import time

import pytz
import humanize
import dateutil
import iso8601


class Time(object):
    def __init__(
            self,
            year=1970,
            month=1,
            day=1,
            hour=0,
            minute=0,
            seconds=0,
            tz=None,
            local=None):
        if tz and local:
            raise ValueError("Either local or a specific timezone")

        tzinfo = pytz.UTC
        if tz:
            tzinfo = pytz.timezone(tz)
        elif local:
            tzinfo = dateutil.tzlocal()

        dt = datetime.datetime(
            year, month, day, hour, minute, seconds, tzinfo=tzinfo)
        self._dt = dt.astimezone(pytz.UTC)

    @classmethod
    def from_timestamp(cls, ts):
        return cls.from_datetime(*datetime.datetime.fromtimestamp(ts))

    @classmethod
    def from_datetime(cls, dt):
        return cls(*dt.timetuple())

    @classmethod
    def from_str(cls, s, format=None, tz=None, local=None):
        if tz and local:
            raise ValueError("Either local or a specific timezone")

        if format is None:
            dt = iso8601.parse_date(s)
        else:
            dt = datetime.strptime(s, format)

        if (tz or local) and dt.tzinfo is not None:
            raise ValueError("Timezone was in string")

        if tz:
            dt = pytz.timezone(tz).localize(dt)
        elif local:
            dt = dateutil.tzlocal().localize(dt)

        dt = dt.astimezone(pytz.UTC)
        return cls.from_datetime(dt)

    @property
    def year(self):
        return self._dt.year

    @property
    def month(self):
        return self._dt.month

    @property
    def day(self):
        return self._dt.day

    @property
    def hour(self):
        return self._dt.hour

    @property
    def minute(self):
        return self._dt.minute

    @property
    def second(self):
        return self._dt.second

    def _localized_dt(tz=None, local=False):
        if local:
            return self._dt.astimezone(dateutil.tzlocal())
        elif tz:
            return self._dt.astimezone(pytz.timezone(tz))
        else:
            return self._dt

    def to_str(self, format=None, tz=None, local=False):
        dt = self._localized_dt(tz=tz, local=local)

        if format:
            return dt.strftime(format)
        else:
            return dt.isoformat()

    def to_datetime(self, tz=None, local=None):
        return self._localized_dt(tz=tz, local=local)

    def to_human(self, tz=None, local=None):
        return humanize.naturaltime(self._localized_dt(tz=tz, local=local))


class TimeSpan(object):
    def __init__(self, start_t, end_t):
        self.start_t = start_t
        self.end_t = end_t

    def __iter__(self):
        yield self.start_t
        yield self.end_t


class TimeInterval(object):
    def __init__(self, seconds=None, minutes=None, hours=None):
        self.seconds = 0

        if seconds:
            self.seconds += seconds
        if minutes:
            self.seconds += minutes * 60
        if hours:
            self.seconds += minutes * 60 * 60

    @classmethod
    def from_date(self, d):
        raise NotImplementedError


class TimeIterator(object):
    def __init__(self, span, interval):
        self.span = span
        self.interval = interval

    def __iter__(self):
        next_t, end_t = span

        while next_t < end_t:
            yield next_t
            next_t = next_t + self.interval
