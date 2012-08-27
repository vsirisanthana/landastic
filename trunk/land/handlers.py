import datetime
import logging
import os
import json

import jinja2
import webapp2
from google.appengine.api import users
from google.appengine.ext import db
from webapp2_extras.appengine.users import login_required

from .models import Land, Price
from .parsers import parse
from .utils import to_dict


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    variable_start_string='{$',
    variable_end_string='$}',
)


loge = lambda *args: logging.error(*args)


def clean_data(data, datatype):
    pass

def clean_float(data):
    try:
        float(data)
    except TypeError:
        pass


def clean_land_data(params):
#    loge('==============================================================================================')
    dd = {}

    for property_name, property_class in Land.properties().items():
        if params.has_key(property_name):
            dd[property_name] = params[property_name]

    data = {}
    if params.has_key('name'): data['name'] = params['name']
    if params.has_key('description'): data['description'] = params['description']
    if params.has_key('location'):
        location = params['location']
        lat, lng = [l.strip() for l in location.split(',')]
        data['location'] = db.GeoPt(lat, lng)
    if params.has_key('features'): data['features'] = params['features']
    if params.has_key('area'):
        try:
            area = float(params['area'])
        except (TypeError, ValueError):
            area = None
        data['area'] = area
    if params.has_key('price'):
        try:
            price = float(params['price'])
        except (TypeError, ValueError):
            price = None
        data['price'] = price
    return data

def clean_price_data(params):
    data = {
        'type': params['type'],
        'value': params['value'],
        'date': datetime.datetime.strptime(params['date'], '%Y-%m-%d %H:%M:%S')
    }
    return data


class LandInstanceHandler(webapp2.RequestHandler):

#    def __init__(self, resource):
#        self.resource = resource

    def get(self, key):
        try:
            land = Land.get(key)
        except db.BadKeyError:
            self.error(404)
            self.response.out.write(json.dumps('Error 404 Not Found'))
        else:
            ask_prices = Price.all().ancestor(land).filter('type =', 'ask').order('-date')
            bid_prices = Price.all().ancestor(land).filter('type =', 'bid').order('-date')
            market_prices = Price.all().ancestor(land).filter('type =', 'market').order('-date')

            land.ask_price = ask_prices.get()
            land.bid_price = bid_prices.get()
            land.market_price = market_prices.get()

#            print land.ask_price


#            land.latest_ask_price = ask_prices[0] if ask_prices else None
#            land.latest_bid_price = bid_prices[0] if bid_prices else None
#            land.latest_market_price = market_prices[0] if market_prices else None

            land_dict = to_dict(land)
            land_dict.update({
                'latest_ask_price': ask_prices.get(),
                'latest_bid_price': bid_prices.get(),
                'latest_market_price': market_prices.get(),
            })

            self.response.out.write(json.dumps(land_dict))
        self.response.headers['Content-Type'] = 'application/json'

    @parse
    def put(self, key):
        try:
            land = Land.get(key)
#            logging.error(dir(land))
        except db.BadKeyError:
            self.error(404)
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps('Error 404 Not Found'))
        else:
            data = clean_land_data(self.request.CONTENT)
            for k, v in data.items():
                setattr(land, k, v)
            land.put()

            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps(to_dict(land)))

    def delete(self, key):
        try:
            land = Land.get(key)
        except db.BadKeyError:
            self.error(404)
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps('Error 404 Not Found'))
        else:
            land.delete()
            self.response.set_status(204)
            del self.response.headers['Content-Type']


class LandListOrCreateHandler(webapp2.RequestHandler):

#    @login_required
    def get(self):
        lands = [to_dict(land) for land in Land.gql('ORDER BY last_modified DESC')]
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(lands))

    @parse
    def post(self):
        data = clean_land_data(self.request.CONTENT)
        land = Land(**data)
        land.put()

        self.response.set_status(201)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(to_dict(land)))


class LandPriceListOrCreateHandler(webapp2.RequestHandler):

    def get(self, key):
        try:
            land = Land.get(key)
        except db.BadKeyError:
            self.error(404)
            self.response.out.write(json.dumps('Error 404 Not Found'))
        else:
            prices = Price.all().ancestor(land).order('-date')
            prices = [to_dict(price) for price in prices]
            self.response.out.write(json.dumps(prices))
        self.response.headers['Content-Type'] = 'application/json'

    @parse
    def post(self, key):
        try:
            land = Land.get(key)
        except db.BadKeyError:
            self.error(404)
            self.response.out.write(json.dumps('Error 404 Not Found'))
        else:
            data = clean_price_data(self.request.CONTENT)
            price = Price(parent=land, **data)
            price.put()

            self.response.set_status(201)
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(json.dumps(to_dict(price)))


from webob.multidict import MultiDict

class AppHandler(webapp2.RequestHandler):

    @login_required
    def get(self):
        user = users.get_current_user()
        logout_url = users.create_logout_url(self.request.uri)

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render({
            'nickname': user.nickname(),
            'logout_url': logout_url,
        }))

class TemplateHandler(webapp2.RequestHandler):

    @login_required
    def get(self, name):
        template = jinja_environment.get_template(name)
        self.response.out.write(template.render())