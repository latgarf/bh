
import datetime, calendar

def to_epoch(t):
    return calendar.timegm(t.utctimetuple()) + t.microsecond/1000000

def to_epoch_str(t):
    return '%.3f' % to_epoch(t)

def utc_now():
    return datetime.datetime.utcnow()

def now_epoch():
    return to_epoch(utc_now())

def now_epoch_str():
    return '%.3f' % now_epoch()


if __name__ == "__main__":
    print(now_epoch_str())
