import datetime
import time

from google.appengine.api import users
from google.appengine.ext import db

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)

def to_dict(model):
    output = {}

    for key, prop in model.properties().iteritems():
        value = getattr(model, key)

        if value is None or isinstance(value, SIMPLE_TYPES):
            output[key] = value
        elif isinstance(value, datetime.date):
            # Convert date/datetime to ms-since-epoch ("new Date()").
            ms = time.mktime(value.utctimetuple())
            ms += getattr(value, 'microseconds', 0) / 1000
            output[key] = int(ms)

            output[key] = str(value)
        elif isinstance(value, db.GeoPt):
#            output[key] = {'lat': value.lat, 'lon': value.lon}
            output[key] = '%s,%s' % (value.lat, value.lon)
        elif isinstance(value, db.Model):
            output[key] = to_dict(value)
        elif isinstance(value, users.User):
            output[key] = value.nickname()
        else:
            raise ValueError('cannot encode ' + repr(prop))

    output['key'] = unicode(model.key())

    return output