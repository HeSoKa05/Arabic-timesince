"""
the ar_timesince and ar_timeuntile functioins are modified copies of "timesince" and "timeuntile" from Djando freamwork
the original functions can be found in django.utils.timesince import timesince
in this file, I combined some functions and lines such as: "utc"
that is imported in the original module which are needed in order "timesince" function works as expected.
"""

import datetime, calendar
import pytz
from datetime import timedelta


utc = pytz.utc


# Arabic language has 6 plural forms, see: https://arabeyes.org/Plural_Forms
# every chunk has multiple forms according to Arabic plural forms
TIME_STRINGS = {
        'year': ['عام واحد', 'عامان', '%d أعوام', '%d عاماً', '%d عام'],
        'month': ['شهر واحد', 'شهران', '%d أشهر', '%d شهراً', '%d شهر'],
        'week': ['أسبوع واحد', 'أسبوعان', '%d أسابيع', '%d أسبوعاً', '%d أسبوع'],
        'day': ['يوم واحد', 'يومان', '%d أيام', '%d يوماً', '%d يوم'],
        'hour': ['ساعة واحدة', 'ساعتان', '%d ساعات', '%d ساعةً', '%d ساعة'],
        'minute': ['دقيقة واحدة', 'دقيقتان', '%d دقائق', '%d ًدقيقة', '%d دقيقة'],
        'second': ['ثانية واحدة', 'ثانيتان', '%d ثواني', '%d ثانيةً', '%d ثانية']
    }

TIMESINCE_CHUNKS = (
    (60 * 60 * 24 * 365, 'year'),
    (60 * 60 * 24 * 30, 'month'),
    (60 * 60 * 24 * 7, 'week'),
    (60 * 60 * 24, 'day'),
    (60 * 60, 'hour'),
    (60, 'minute'),
)

def is_aware(value):
    return value.utcoffset() is not None



def ar_timing(time_strings, name, count):
    if count == 1:
        return time_strings[name][0]
    elif count == 2:
        return time_strings[name][1]
    else:
        return time_strings[name][arplural(count)] % count


# split the number into digits inside list
def todigits(num):
    result = [int(a) for a in str(num)]
    if len(result) == 1:
        result.insert(0,0)
    return result

# return to last digits of a number
def lasttowdigits(num):
    return todigits(num)[-2]*10 + todigits(num)[-1]


# I took just 5 forms of plural because there's no need for the zero case, e.g: "0 عام" it has no sence
# if there for example 0 year or 0 month, it wouldn't be mentioned ar all.

def arplural(digit):
    if digit == 1:
        return 0
    if digit == 2:
        return 1
    if lasttowdigits(digit) >= 3 and lasttowdigits(digit) <=10:
        return 2
    if lasttowdigits(digit) >=11 and lasttowdigits(digit) <= 99:
        return 3
    if digit >= 100 and (lasttowdigits(digit) == 0 or lasttowdigits(digit) == 1 or lasttowdigits(digit) == 2):
        return 4
        

def ar_timesince(d, now=None, reversed=False, depth=2):
    """
    Adapted from
    https://web.archive.org/web/20060617175230/http://blog.natbat.co.uk/archive/2003/Jun/14/time_since
    """
    time_strings = TIME_STRINGS

    if depth <= 0:
        raise ValueError('depth must be greater than 0.')
    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    now = now or datetime.datetime.now(utc if is_aware(d) else None)

    if reversed:
        d, now = now, d
    delta = now - d

    # Deal with leapyears by subtracing the number of leapdays
    leapdays = calendar.leapdays(d.year, now.year)
    if leapdays != 0:
        if calendar.isleap(d.year):
            leapdays -= 1
        elif calendar.isleap(now.year):
            leapdays += 1
    delta -= datetime.timedelta(leapdays)

    # ignore microseconds
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return 'لا شيء بعد'
    for i, (seconds, name) in enumerate(TIMESINCE_CHUNKS):
        count = since // seconds
        if count != 0:
            break
    result = ar_timing(time_strings, name, count)
    if i + 1 < len(TIMESINCE_CHUNKS):
        # Now get the second item
        seconds2, name2 = TIMESINCE_CHUNKS[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            result += ' و' + ar_timing(time_strings, name2, count2)
    return result


def ar_timeuntil(d, now=None):
    """
    Like ar_timesince, but return a string measuring the time until the given time.
    """
    return ar_timesince(d, now, reversed=True)
