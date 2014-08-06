dmc
========

`dmc` is python library for date and time manipulation.

Usage of standard library modules such as `datetime`, `time`, `pytz` etc is dangerous and error prone.

This library is very opinionated about how to treat dates, times and intervals
so as to prevent developers from shooting themselves in the foot. Also, the API
is quote a bit more convinient for most use cases.

Overview
---------

dmc is really just a wrapper around several other python libraries, but does so
in a way that makes using these libraries safe.

Some things to keep in mind:

  * There is no such thing as a naive time. ALL times involve a timezone, and that timezone is UTC.
  * The only time we deal with non-UTC timezones is when we parse or display a time.
  * We support math with dates, and math with times, but you can't do date math with times.
    For example: You can't add "1 day" to 2014-03-28 02:00:00, because that
    doesn't actually make sense. Do you mean add 24 hours? Then do that. Did
    you mean you want 02:00:00 on 3/29, sure we can do that, but you have to
    decide.

We have a few primary objects:

  * Time - Represents a precise time in UTC.
  * TimeInterval - Represents a change in time, like 10 minutes, or 4000 hours.
  * TimeSpan - a range of Times of some TimeInterval length
  * TimeIterator - generates time instances based on a TimeSpan and a TimeInterval
  * Date - Represents a calendar date. Only the modern Gregorian calendar is supported.
  * DateInterval - Represents a change in calendar date, like '2 days', 'next month', or 'next monday'
  * DateSpan - a range of dates of some DateInterval.
  * DateIterator - genreates dates based on DateSpan and an DateInterval



Usage
----------


    >> start_t = dmc.Time.now()
    >> print start_t
    "2014-03-29T20:16:58.265249Z"

    >> print start.to_str(tz='Americas/Los_Angeles')
    "2014-03-29T12:16:58.265249-7:00"

    >> print start.to_str(local=True)
    "2014-03-29T12:16:58.265249-7:00"

    >> start.to_str("YYYY-MM-DD HH:MM", tz='Americas/Los_Angeles')
    "2014-03-29 12:16"

    >> print start_t.to_timestamp()
    1396120755.748726

    >> print start_t.to_human()
    "10 minutes ago"

    >> start_t = dmc.Time.from_timestamp(1396120755.748726)

    >> print start_t.to_datetime()
    datetime.datetime(2014, 3, 29, 12, 16, 58, 0, tzinfo=<UTC>)

    >> d = dmc.Date(2014, 3, 28)
    >> print d
    "2014-03-28"

    >> dmc.Date.from_str("3/28/2014")
    dmc.Date(2014, 28, 3)

    >> start_t, _ = dmc.TimeSpan.from_date(d)
    >> print start_t
    "2014-03-28T00:00:00Z"

    # 3 weeks from now
    >> d += dmc.DateInterval(weeks=3)

    # Next Sunday
    >> d += dmc.DateInterval(weekday=0)

    >> start_t, end_t = dmc.TimeSpan.from_date(d)

    >> t = dmc.Time.now()
    >> t += dmc.TimeInterval(minutes=30)

    >> today_span = dmc.Date.today().to_timespan()
    >> for t in dmc.TimeIterator(today_span, dmc.TimeInterval(hours=1)):
    >>    print t
    "2014-03-28T00:00:00Z"
    "2014-03-28T01:00:00Z"
    "2014-03-28T02:00:00Z"
    ....


Testing
----------

When you're working with date and time sensitive code, it's often very helpful
to be able to mock out the current time or date. `dmc` makes this easy:

    >> dmc.set_mock_time(dmc.Time().now() - dmc.TimeInterval(hours=1))
    >> dmc.clear_mock_time()

Or, with a friendly context manager:

    >> with dmc.MockTime(...):
    .... pass


What's wrong with datetime
-----------

This fun old wiki page is enlightening: https://wiki.python.org/moin/WorkingWithTime

Datetime was supposed to be the solution. I still remember when I stumbed
across mx.Datetime. Mind blown. Such a better world. (datetime was added in
python 2.3, in 2003, over 10 years ago). You'd think that dealing with dates
and times would be solved problem. But twice a year I wake up to the collective
"oh shit" as developers remember daylight savings time.

There is also [PEP-431](http://legacy.python.org/dev/peps/pep-0431/) that
attempts to fix datetime timezones. Or is it just patching over how insane it
is to handle timezones in this way?

There are also a lot of glaring holes in the API datetime provides us. We fill
those holes with a cornocopia of several other modules.  Basically, if you're
doing anything remotely complex with dates and times you need to understand and
make us of:

  * datetime
  * time
  * calendar
  * pytz
  * dateutil

`dmc` attempts to combine all these together into a consistent interface so you don't have to.

For specific examples, try these:

#### timestamps

It's easy to create a a datetime from a timestamp:

    >> d = datetime.datetime.fromtimestamp(12312412.0)

Oh wait, what timezone was that in? What we should have done was

    >> d = datetime.datetime.utcfromtimestamp(12312412.0)

Pop, quiz, how do you convert back?

    >> import time
    >> time.mktime(d.timetuple())

Or wait, did I mean:

    >> time.mktime(d.utctimetuple())

#### formatting / parsing

    >> d.isoformat()
    '2014-04-17T15:32:01.219333'

Now how do I parse an isoformat? There are several solutions on stackoverflow.

    >> datetime.datetime.strptime("2014-04-17T15:32:01", "%Y-%m-%dT%H:%M:%S" )

But of course parsing iso8601 is more complicated than that:

    >> import re
    >> s = "2008-09-03T20:56:35.450686Z"
    >> d = datetime.datetime(*map(int, re.split('[^\d]', s)[:-1]))

Ok, there are some 3rd party libraries:

    >> dateutil.parser.parse('2014-04-17T15:32:01.219333Z')

Of course you need to be real careful with this library, if there is something
it doesn't recognize you'll just get a datetime filled in with values from the
current time (!!!! wtf)

Oh good, there is a python module for JUST THIS ONE FORMAT:

    >> import iso8601
    >> iso8601.parse_date("2007-01-25T12:00:00Z")
       datetime.datetime(2007, 1, 25, 12, 0, tzinfo=<iso8601.iso8601.Utc ...>)

I don't even want to think about whether `iso8601.iso8601.Utc == pytz.UTC`.

#### timezones

    >> datetime.datetime.now()

What timezone is this in?

Oh right, what I actually need to do is:

    >> import pytz
    >> d = pytz.UTC.localize(datetime.datetime.utcnow())

How about some arithmetic:

    >> now() + datetime.timedelta(days=1)

Is this 24 hours from now? Is this the same number hours since midnight but the
next calendar day? Unfortunately the difference between these interpretations
only becomes obvious twice a year, in only some political regions of the world.

What if I wanted to enumerate time ranges for a day in localtime, and then run
some queries that are in UTC.

    >> import pytz
    >> tz = pytz.timezone('US/Pacific')
    >> start_dt = datetime.datetime(2014, 3, 9, 0, 0, 0, tzinfo=tz)
    >> end_dt = start_dt + datetime.timedelta(days=1)
    >> d = start_dt

    while d < end_dt:
        run_query(d.astimezone(pytz.UTC), d.astimezone(pytz.UTC) + datetime.timedelta(hours=1))
        d += datetime.timedelta(hours=1)

How many errors can you spot?

Oh, my favorite:

    >> import pytz
    >> tz = pytz.timezone('US/Pacific')
    >> start_dt = datetime.datetime(2014, 3, 6, 0, 0, 0, tzinfo=tz)

    >> d = start_dt
    >> for _ in range(7):
    ...   print d
    ...   d += datetime.timedelta(days=1
    2014-03-06 00:00:00-08:00
    2014-03-07 00:00:00-08:00
    2014-03-08 00:00:00-08:00
    2014-03-09 00:00:00-08:00
    2014-03-10 00:00:00-08:00
    2014-03-11 00:00:00-08:00
    2014-03-12 00:00:00-08:00

See anything wrong here? 2014-03-10 00:00:00-08:00 doesn't make any sense.
Because on the 2014-03-10, the timezone should be -07:00. There are fun
switcheroo ways around this:

    >> d = start_dt
    >> for _ in range(7):
    ...   print d.astimezone(pytz.UTC).astimezone(pytz.timezone('US/Pacific'))
    ...   d += datetime.timedelta(days=1)

This is common enough that pytz actually provides a function for it:


    >> print pytz.timezone('US/Pacific').normalize(d)


Project Status
----------------

*Experimental*. Still estabilishing interfaces.

Basic `Date` and `Time` formatting and parsing are written and tested.

`Intervals` and `Span` are being actively developed.

DMC still requires some real world use before APIs are firmly set.
