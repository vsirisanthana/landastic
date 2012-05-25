import simplejson
import webapp2

from google.appengine.ext import db

from .models import Land
from .utils import to_dict


import jinja2
import os

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
                features = body['features']
            else:
                name = self.request.get('name')
                location = self.request.get('location')
                features = self.request.get('features')

            lat, lng = [l.strip() for l in location.split(',')]

            land.name = name
            land.location = db.GeoPt(lat, lng)
            land.features = features
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


from google.appengine.api import users
#def login_required(method):
#    user = users.get_current_user()
#    if user:
#        return method
#    else:
#        return False

from webapp2_extras.appengine.users import login_required

#from google.appengine.ext.webapp.util import login_required

class LandListOrCreateHandler(webapp2.RequestHandler):

#    @login_required
    def get(self):
        lands = [to_dict(land) for land in Land.gql('ORDER BY last_modified DESC')]
        self.response.headers['Content-Type'] = 'application/json'
#        self.response.out.write(simplejson.dumps({'results': lands}))

        url = users.create_logout_url(self.request.uri)
#        lands.append(url)

        self.response.out.write(simplejson.dumps(lands))

    def post(self):
        if self.request.headers['Content-Type'] == 'application/json':
            body = simplejson.loads(self.request.body)
            name = body['name']
            location = body['location']
            features = body['features']
        else:
            name = self.request.get('name')
            location = self.request.get('location')
            features = self.request.get('features')

        lat, lng = [l.strip() for l in location.split(',')]

        land = Land(name=name, location=db.GeoPt(lat, lng), features=features)
        land.put()

        self.response.set_status(201)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(simplejson.dumps(to_dict(land)))


class MainHandler(webapp2.RequestHandler):

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