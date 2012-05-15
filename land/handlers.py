import logging
import simplejson
import webapp2

from google.appengine.ext import db

from .models import Land
from .utils import to_dict


class InstanceLandHandler(webapp2.RequestHandler):

#    def __init__(self, resource):
#        self.resource = resource

    def get(self, key):
        try:
            land = Land.get(key)
        except db.BadKeyError:
            self.error(404)
        else:
            self.response.out.write(simplejson.dumps(to_dict(land)))
        self.response.headers['Content-Type'] = 'application/json'

    def put(self, key):
        try:
            land = Land.get(key)
        except db.BadKeyError:
            self.error(404)
        else:
            if self.request.headers['Content-Type'] == 'application/json':
                body = simplejson.loads(self.request.body)
                name = body['name']
                location = body['location']
            else:
                name = self.request.get('name')
                location = self.request.get('location')

            lat, lng = [l.strip() for l in location.split(',')]

            land.name = name
            land.location = db.GeoPt(lat, lng)
            land.put()

            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(simplejson.dumps(to_dict(land)))

    def delete(self, key):
        try:
            land = Land.get(key)
        except db.BadKeyError:
            self.error(404)
        else:
            land.delete()
            self.response.set_status(204)
        self.response.headers['Content-Type'] = 'application/json'


class ListOrCreateLandHandler(webapp2.RequestHandler):

    def get(self):
        lands = [to_dict(land) for land in Land.gql('')]
        self.response.headers['Content-Type'] = 'application/json'
#        self.response.out.write(simplejson.dumps({'results': lands}))
        self.response.out.write(simplejson.dumps(lands))

    def post(self):
        if self.request.headers['Content-Type'] == 'application/json':
            body = simplejson.loads(self.request.body)
            name = body['name']
            location = body['location']
        else:
            name = self.request.get('name')
            location = self.request.get('location')

        lat, lng = [l.strip() for l in location.split(',')]

        land = Land(name=name, location=db.GeoPt(lat, lng))
        land.put()

        self.response.set_status(201)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(simplejson.dumps(to_dict(land)))
