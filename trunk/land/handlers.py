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


def clean_land_data(params):
    data = {}
    if params.has_key('name'): data['name'] = params['name']
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