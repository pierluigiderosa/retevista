from django.template import Library
import time
register = Library()

@register.filter
def print_timestamp(timestamp):
    try:
        #assume, that timestamp is given in seconds with decimal point
        ts = int(timestamp)
    except ValueError:
        return None
    # return datetime.datetime.utcfromtimestamp(ts)
    return time.strftime("%d %m %Y", time.gmtime(ts))

# register.filter(print_timestamp)