import simplejson
import unittest
import webtest

from google.appengine.ext import testbed

from ..models import Land
from ..urls import app


class TestLandListOrCreateHandler(unittest.TestCase):

    def setUp(self):
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_list_empty(self):
        response = self.testapp.get('/api/lands')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(simplejson.loads(response.normal_body), [])

    def test_list_one_land(self):
        land = Land(name='Wonderland', location='18.769937,99.003156', geom='NO VALIDATION YET')
        land.put()

        response = self.testapp.get('/api/lands')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_json = simplejson.loads(response.normal_body)
        self.assertEqual(len(response_json), 1)

        response_land = response_json[0]
        self.assertEqual(response_land['name'], 'Wonderland')
        self.assertEqual(response_land['location'], '18.769937,99.003156')
        self.assertEqual(response_land['geom'], 'NO VALIDATION YET')

    def test_list_multiple_lands(self):
        land0 = Land(name='Wonderland', location='18.769937,99.003156', geom='NO VALIDATION YET')
        land0.put()
        land1 = Land(name='Monkey Club', location='18.797771,98.967979', geom='NO VALIDATION AS YET')
        land1.put()

        response = self.testapp.get('/api/lands')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_json = simplejson.loads(response.normal_body)
        self.assertEqual(len(response_json), 2)

        response_land0 = response_json[0]
        self.assertEqual(response_land0['name'], 'Neverland')
        self.assertEqual(response_land0['location'], '18.797771,98.967979')
        self.assertEqual(response_land0['geom'], 'NO VALIDATION AS YET')

        response_land1 = response_json[1]
        self.assertEqual(response_land0['name'], 'Wonderland')
        self.assertEqual(response_land0['location'], '18.769937,99.003156')
        self.assertEqual(response_land0['geom'], 'NO VALIDATION YET')

    def test_create(self):
        response = self.testapp.post('/api/lands', {
            'name': 'Wonderland',
            'location': '18.769937,99.003156',
            'geom': 'NO VALIDATION YET',
        })
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.content_type, 'application/json')

        response_land = simplejson.loads(response.normal_body)
        self.assertEqual(response_land['name'], 'Wonderland')
        self.assertEqual(response_land['location'], '18.769937,99.003156')
        self.assertEqual(response_land['geom'], 'NO VALIDATION YET')
