import logging
import os
import json

import jinja2
import webapp2
from google.appengine.api import users
from google.appengine.ext import db
from webapp2_extras.appengine.users import login_required

from .models import Land
from .parsers import parse
from .utils import to_dict


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    variable_start_string='{$',
    variable_end_string='$}',
)


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
            self.response.out.write(json.dumps(to_dict(land)))
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
            name = self.request.CONTENT.get('name')
            location = self.request.CONTENT.get('location')
            features = self.request.CONTENT.get('features')
            area = self.request.CONTENT.get('area')
            price = self.request.CONTENT.get('price')

            lat, lng = [l.strip() for l in location.split(',')]
            if area: area = float(area)
            if price: price = float(price)

            land.name = name
            land.location = db.GeoPt(lat, lng)
            land.features = features
            if area: land.area = area
            land.price = price
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
        name = self.request.CONTENT.get('name')
        location = self.request.CONTENT.get('location')
        features = self.request.CONTENT.get('features')
        area = self.request.CONTENT.get('area')
        price = self.request.CONTENT.get('price')

        lat, lng = [l.strip() for l in location.split(',')]
        if area: area = float(area)
        if price: price = float(price)

        land = Land(
            name = name,
            location = db.GeoPt(lat, lng),
            features = features,
            area = area,
            price = price,
        )
        land.put()

        self.response.set_status(201)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(to_dict(land)))

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