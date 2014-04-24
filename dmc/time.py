from __future__ import absolute_import

# -*- coding: utf-8 -*-

"""
This module contains the set of dmcs's exceptions

:copyright: (c) 2014 by Rhett Garber.
:license: ISC, see LICENSE for more details.

"""
import datetime
import time
import math
import sys

import pytz
import dateutil.tz
import iso8601

from . import human
from . testing import get_mock_now


MICROSECS_PER_SEC = 1000000


class Time(object):
    __slots__ = ['_dt']

    def __init__(
            self,
            year=1970,
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tz=None,
            local=None):
        if tz and local:
            raise ValueError("Either local or a specific timezone")

        tzinfo = pytz.UTC
        if tz:
            tzinfo = pytz.timezone(tz)
        elif local:
            tzinfo = dateutil.tz.tzlocal()

        dt = datetime.datetime(
            year, month, day, hour, minute, second, microsecond, tzinfo=tzinfo)

        if tzinfo:
            try:
                dt = tzinfo.normalize(dt)
            except AttributeError:
                pass

        self._dt = dt.astimezone(pytz.UTC)

    @classmethod
    def now(cls):
        return get_mock_now() or cls.from_datetime(datetime.datetime.utcnow())

    @classmethod
    def from_timestamp(cls, ts):
        # fromtimestamp doesn't handle the float part of a timestamp, so if it
        # exists, we'll need to patch it in.
        ts_ms = int(round((ts - math.floor(ts)) * MICROSECS_PER_SEC))

        dt = datetime.datetime.utcfromtimestamp(ts)
        if ts_ms:
            dt = dt.replace(microsecond=ts_ms)

        return cls.from_datetime(dt)

    @classmethod
    def from_datetime(cls, dt):
        if dt.tzinfo is not None:
            dt = dt.astimezone(pytz.UTC)

        return cls(
            dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second,
            dt.microsecond)

    @classmethod
    def from_str(cls, s, format=None, tz=None, local=None):
        if tz and local:
            raise ValueError("Either local or a specific timezone")

        if format is None:
            dt = iso8601.parse_date(s, default_timezone=None)
        else:
            dt = datetime.strptime(s, format)

        if (tz or local) and dt.tzinfo is not None:
            raise ValueError("Timezone was in string")

        if tz:
            tzinfo = pytz.timezone(tz)
            dt = tzinfo.localize(dt, is_dst=None)
        elif local:
            dt = dt.replace(tzinfo=dateutil.tz.tzlocal())
        elif dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)

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

    @property
    def microsecond(self):
        return self._dt.microsecond

    def __unicode__(self):
        return self.to_str()

    def __repr__(self):
        return '<dmc.Time({}, {}, {}, {}, {}, {}, {}>'.format(
            self.year, self.month, self.day, self.hour, self.minute,
            self.second, self.microsecond)

    def _localized_dt(self, tz=None, local=False):
        if local:
            return self._dt.astimezone(dateutil.tz.tzlocal())
        elif tz:
            tzinfo = pytz.timezone(tz)
            return tzinfo.normalize(self._dt.astimezone(tzinfo))
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

    def to_timestamp(self):
        ts = time.mktime(self._dt.utctimetuple())
        ts += (1.0 * self._dt.microsecond) / MICROSECS_PER_SEC
        return ts

    def to_human(self):
        return human.naturaltime(self._dt.replace(tzinfo=None))

    def __add__(self, other):
        if isinstance(other, TimeInterval):
            return Time.from_datetime(
                self._dt +
                datetime.timedelta(
                    seconds=other.seconds, microseconds=other.microseconds))
        elif isinstance(other, (int, float)):
            return self + TimeInterval(seconds=other)
        else:
            raise NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, TimeInterval):
            return Time.from_datetime(
                self._dt -
                datetime.timedelta(
                    seconds=other.seconds, microseconds=other.microseconds))
        elif isinstance(other, (int, float)):
            return self - TimeInterval(seconds=other)
        else:
            raise NotImplemented

    def __cmp__(self, other):
        if isinstance(other, Time):
            return cmp(self.to_datetime(), other.to_datetime())
        elif isinstance(other, datetime.datetime):
            return cmp(self.to_datetime(), other)
        else:
            raise NotImplemented


class TimeSpan(object):
    __slots__ = ['start', 'end']

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __iter__(self):
        yield self.start
        yield self.end

    def __getitem__(self, key):
        if key == 0:
            return self.start
        elif key == 1:
            return self.end
        else:
            raise KeyError

    def __repr__(self):
        return "<dmc.TimeSpan({}, {})>".format(self.start, self.end)

    def __str__(self):
        return "{} to {}".format(self.start, self.end)


class TimeInterval(object):
    __slots__ = ['seconds', 'microseconds']

    def __init__(
            self,
            seconds=None,
            minutes=None,
            hours=None,
            microseconds=None):

        self.microseconds = 0
        self.seconds = 0

        if seconds:
            # For convinience, we'll accept a float for seconds and strip out
            # the microseconds
            self.microseconds += int(
                round(
                    (seconds - math.floor(seconds)) * MICROSECS_PER_SEC))

            self.seconds += int(math.floor(seconds))

        if minutes:
            self.seconds += minutes * 60

        if hours:
            self.seconds += hours * 60 * 60

        if microseconds:
            self.microseconds += microseconds

            if self.microseconds >= MICROSECS_PER_SEC:
                self.seconds += self.microseconds // MICROSECS_PER_SEC
                self.microseconds = self.microseconds % MICROSECS_PER_SEC

    @classmethod
    def from_timedelta(self, td):
        # Timedelta's store as (days, seconds, microseconds).  TimeInterval
        # deals in just seconds and microseconds. Do we lose anything here?
        # Obviously we have the same resolution, so the only question is if
        # sys.maxint seconds isn't big enough for us. Unlikely on 64bit.
        if sys.maxint / (60*60*24) < td.days:
            raise ValueError("Platform maxint isn't large enough")

        seconds = (td.days * 60*60*24) + td.seconds
        microseconds = td.microseconds

        return TimeInterval(seconds=seconds, microseconds=microseconds)

    def __int__(self):
        if self.microseconds:
            return int(round(float(self)))
        else:
            assert type(self.seconds), int
            return self.seconds

    def __float__(self):
        return self.seconds + (1.0 * self.microseconds / MICROSECS_PER_SEC)

    def __str__(self):
        seconds = self.seconds

        hours = seconds // (60 * 60)
        seconds -= hours * 60 * 60

        minutes = seconds // 60
        seconds -= minutes * 60

        seconds += 1.0 * self.microseconds / MICROSECS_PER_SEC

        return "{:=+03d}:{:02d}:{:04.1f}".format(hours, minutes, seconds)

    def __add__(self, other):
        if isinstance(other, type(self)):
            seconds = other.seconds + self.seconds
            microseconds = other.microseconds + self.microseconds
            return TimeInterval(seconds=seconds, microseconds=microseconds)
        elif isinstance(other, (int, float)):
            seconds = float(self) + other
            return TimeInterval(seconds=seconds)
        elif isinstance(other, Time):
            return Time.from_datetime(
                other.to_datetime() +
                datetime.timedelta(
                    seconds=self.seconds, microseconds=self.microseconds))
        else:
            raise NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, type(self)):
            seconds = self.seconds - other.seconds
            microseconds = self.microseconds - other.microseconds
            return TimeInterval(seconds=seconds, microseconds=microseconds)
        elif isinstance(other, (int, float)):
            seconds = float(self) - other
            return TimeInterval(seconds=seconds)
        else:
            raise NotImplemented

    def __rsub__(self, other):
        if isinstance(other, type(self)):
            raise NotImplemented
        elif isinstance(other, (int, float)):
            return other - float(self)
        else:
            raise NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return TimeInterval(
                seconds=self.seconds * other,
                microseconds=self.microseconds * other)
        else:
            raise NotImplementedError

    def __div__(self, other):
        if isinstance(other, (int, float)):
            return TimeInterval(
                seconds=self.seconds / float(other),
                microseconds=self.microseconds / float(other))
        else:
            raise NotImplementedError

    def __abs__(self):
        return TimeInterval(
            seconds=abs(self.seconds), microseconds=abs(self.microseconds))

    def __cmp__(self, other):
        if isinstance(other, TimeInterval):
            return cmp(
                (self.seconds, self.microseconds),
                (other.seconds, other.microseconds))

        raise NotImplemented


class TimeIterator(object):
    __slots__ = ['span', 'interval']

    def __init__(self, span, interval):
        self.span = span
        self.interval = interval

    def __iter__(self):
        next_t, end_t = self.span

        while next_t <= end_t:
            yield next_t
            next_t = next_t + self.interval


class TimeSpanIterator(object):
    __slots__ = ['span', 'interval']

    def __init__(self, span, interval):
        self.span = span
        self.interval = interval

    def __iter__(self):
        next_t, end_t = self.span

        while next_t < end_t:
            yield TimeSpan(next_t, min(next_t + self.interval, end_t))
            next_t = next_t + self.interval
