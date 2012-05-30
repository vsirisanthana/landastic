import logging
import json
import unittest
import webtest

from google.appengine.ext import testbed

from ..models import Land
from ..urls import app


class BaseTestHandler(unittest.TestCase):

    def setUp(self):
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

    def tearDown(self):
        self.testbed.deactivate()


class TestLandListHandler(BaseTestHandler):

    def test_list_empty(self):
        response = self.testapp.get('/api/lands')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(json.loads(response.normal_body), [])

    def test_list_one_land(self):
        land = Land(
            name = 'Wonderland',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
            area = 100.50,
            price = 10000000.50,
        )
        land.put()

        response = self.testapp.get('/api/lands')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_lands = json.loads(response.normal_body)
        self.assertEqual(len(response_lands), 1)

        response_land = response_lands[0]
        self.assertEqual(response_land['key'], str(land.key()))
        self.assertEqual(response_land['name'], 'Wonderland')
        self.assertEqual(response_land['location'], '18.769937,99.003156')
        self.assertEqual(response_land['features'], 'NO VALIDATION YET')
        self.assertEqual(response_land['area'], 100.50)
        self.assertEqual(response_land['price'], 10000000.50)

    def test_list_multiple_lands(self):
        """
        Test land list should be ordered by descending last modified datetime.
        """
        land0 = Land(
            name = 'Wonderland',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
            area = 100.50,
            price = 10000000.50,
        )
        land0.put()
        land1 = Land(
            name = 'Dreamland',
            location = '5.797771,-15.967979',
            features = 'NO VALIDATION AS YET',
            area = 50.50,
            price = 500000.50,
        )
        land1.put()

        response = self.testapp.get('/api/lands')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_lands = json.loads(response.normal_body)
        self.assertEqual(len(response_lands), 2)

        response_land0 = response_lands[0]
        self.assertEqual(response_land0['key'], str(land1.key()))
        self.assertEqual(response_land0['name'], 'Dreamland')
        self.assertEqual(response_land0['location'], '5.797771,-15.967979')
        self.assertEqual(response_land0['features'], 'NO VALIDATION AS YET')
        self.assertEqual(response_land0['area'], 50.50)
        self.assertEqual(response_land0['price'], 500000.50)

        response_land1 = response_lands[1]
        self.assertEqual(response_land1['key'], str(land0.key()))
        self.assertEqual(response_land1['name'], 'Wonderland')
        self.assertEqual(response_land1['location'], '18.769937,99.003156')
        self.assertEqual(response_land1['features'], 'NO VALIDATION YET')
        self.assertEqual(response_land1['area'], 100.50)
        self.assertEqual(response_land1['price'], 10000000.50)

        land0.put()

        response = self.testapp.get('/api/lands')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_lands = json.loads(response.normal_body)
        self.assertEqual(len(response_lands), 2)

        response_land0 = response_lands[0]
        self.assertEqual(response_land0['key'], str(land0.key()))
        self.assertEqual(response_land0['name'], 'Wonderland')
        self.assertEqual(response_land0['location'], '18.769937,99.003156')
        self.assertEqual(response_land0['features'], 'NO VALIDATION YET')
        self.assertEqual(response_land0['area'], 100.50)
        self.assertEqual(response_land0['price'], 10000000.50)

        response_land1 = response_lands[1]
        self.assertEqual(response_land1['key'], str(land1.key()))
        self.assertEqual(response_land1['name'], 'Dreamland')
        self.assertEqual(response_land1['location'], '5.797771,-15.967979')
        self.assertEqual(response_land1['features'], 'NO VALIDATION AS YET')
        self.assertEqual(response_land1['area'], 50.50)
        self.assertEqual(response_land1['price'], 500000.50)


class TestLandCreateHandler(BaseTestHandler):

    def test_create_land(self):
        response = self.testapp.post('/api/lands', {
            'name': 'Wonderland',
            'location': '18.769937,99.003156',
            'features': 'NO VALIDATION YET',
            'area': 100.50,
            'price': 10000000.50,
        })
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.content_type, 'application/json')

        response_land = json.loads(response.normal_body)
        self.assertEqual(response_land['name'], 'Wonderland')
        self.assertEqual(response_land['location'], '18.769937,99.003156')
        self.assertEqual(response_land['features'], 'NO VALIDATION YET')
        self.assertEqual(response_land['area'], 100.50)
        self.assertEqual(response_land['price'], 10000000.50)

        land = Land.get(response_land['key'])
        self.assertEqual(land.name, 'Wonderland')
        self.assertEqual(land.location, '18.769937,99.003156')
        self.assertEqual(land.features, 'NO VALIDATION YET')
        self.assertEqual(land.area, 100.50)
        self.assertEqual(land.price, 10000000.50)

    def test_create_land__application_json(self):
        response = self.testapp.post('/api/lands', json.dumps({
            'name': 'Wonderland',
            'location': '18.769937,99.003156',
            'features': 'NO VALIDATION YET',
            'area': 100.50,
            'price': 10000000.50,
        }), content_type='application/json')
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.content_type, 'application/json')

        response_land = json.loads(response.normal_body)
        self.assertEqual(response_land['name'], 'Wonderland')
        self.assertEqual(response_land['location'], '18.769937,99.003156')
        self.assertEqual(response_land['features'], 'NO VALIDATION YET')
        self.assertEqual(response_land['area'], 100.50)
        self.assertEqual(response_land['price'], 10000000.50)

        land = Land.get(response_land['key'])
        self.assertEqual(land.name, 'Wonderland')
        self.assertEqual(land.location, '18.769937,99.003156')
        self.assertEqual(land.features, 'NO VALIDATION YET')
        self.assertEqual(land.area, 100.50)
        self.assertEqual(land.price, 10000000.50)

    def test_create_land__required_fields(self):
        response = self.testapp.post('/api/lands', {
            'name': 'Wonderland',
            'location': '18.769937,99.003156',
            'features': 'NO VALIDATION YET',
        })
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.content_type, 'application/json')

        response_land = json.loads(response.normal_body)
        self.assertEqual(response_land['name'], 'Wonderland')
        self.assertEqual(response_land['location'], '18.769937,99.003156')
        self.assertEqual(response_land['features'], 'NO VALIDATION YET')

        land = Land.get(response_land['key'])
        self.assertEqual(land.name, 'Wonderland')
        self.assertEqual(land.location, '18.769937,99.003156')
        self.assertEqual(land.features, 'NO VALIDATION YET')


class TestLandGetHandler(BaseTestHandler):

    def test_get_land(self):
        land = Land(
            name = 'Wonderland',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
            area = 100.50,
            price = 10000000.50,
        )
        land.put()

        response = self.testapp.get('/api/lands/%s' % str(land.key()))
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_land = json.loads(response.normal_body)
        self.assertEqual(response_land['name'], 'Wonderland')
        self.assertEqual(response_land['location'], '18.769937,99.003156')
        self.assertEqual(response_land['features'], 'NO VALIDATION YET')
        self.assertEqual(response_land['area'], 100.50)
        self.assertEqual(response_land['price'], 10000000.50)

    def test_get_land__not_found(self):
        response = self.testapp.get('/api/lands/xxx', status=404)
        self.assertEqual(response.status_int, 404)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(json.loads(response.normal_body), 'Error 404 Not Found')


class TestLandPutHandler(BaseTestHandler):

    def test_put_land(self):
        land = Land(
            name = 'Wonderland',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
            area = 100.50,
            price = 10000000.50,
        )
        land.put()

        response = self.testapp.put('/api/lands/%s' % str(land.key()), {
            'name': 'Neverland',
            'location': '20.769937,100.003156',
            'features': 'NO VALIDATION JUST YET',
            'area': 200.50,
            'price': 20000000.50,
        })
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_land = json.loads(response.normal_body)
        self.assertEqual(response_land['name'], 'Neverland')
        self.assertEqual(response_land['location'], '20.769937,100.003156')
        self.assertEqual(response_land['features'], 'NO VALIDATION JUST YET')
        self.assertEqual(response_land['area'], 200.50)
        self.assertEqual(response_land['price'], 20000000.50)

        land = Land.get(land.key())
        self.assertEqual(land.name, 'Neverland')
        self.assertEqual(land.location, '20.769937,100.003156')
        self.assertEqual(land.features, 'NO VALIDATION JUST YET')
        self.assertEqual(land.area, 200.50)
        self.assertEqual(land.price, 20000000.50)

    def test_put_land__application_json(self):
        land = Land(
            name = 'Wonderland',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
            area = 100.50,
            price = 10000000.50,
        )
        land.put()

        response = self.testapp.put('/api/lands/%s' % str(land.key()), json.dumps({
            'name': 'Neverland',
            'location': '20.769937,100.003156',
            'features': 'NO VALIDATION JUST YET',
            'area': 200.50,
            'price': 20000000.50,
        }), content_type='application/json')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_land = json.loads(response.normal_body)
        self.assertEqual(response_land['name'], 'Neverland')
        self.assertEqual(response_land['location'], '20.769937,100.003156')
        self.assertEqual(response_land['features'], 'NO VALIDATION JUST YET')
        self.assertEqual(response_land['area'], 200.50)
        self.assertEqual(response_land['price'], 20000000.50)

        land = Land.get(land.key())
        self.assertEqual(land.name, 'Neverland')
        self.assertEqual(land.location, '20.769937,100.003156')
        self.assertEqual(land.features, 'NO VALIDATION JUST YET')
        self.assertEqual(land.area, 200.50)
        self.assertEqual(land.price, 20000000.50)

    def test_put_land__required_fields(self):
        land = Land(
            name = 'Wonderland',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
            area = 100.50,
            price = 10000000.50,
        )
        land.put()

        response = self.testapp.put('/api/lands/%s' % str(land.key()), {
            'name': 'Neverland',
            'location': '20.769937,100.003156',
            'features': 'NO VALIDATION JUST YET',
        })
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_land = json.loads(response.normal_body)
        self.assertEqual(response_land['name'], 'Neverland')
        self.assertEqual(response_land['location'], '20.769937,100.003156')
        self.assertEqual(response_land['features'], 'NO VALIDATION JUST YET')
        self.assertEqual(response_land['area'], 100.50)
        self.assertEqual(response_land['price'], 10000000.50)

        land = Land.get(land.key())
        self.assertEqual(land.name, 'Neverland')
        self.assertEqual(land.location, '20.769937,100.003156')
        self.assertEqual(land.features, 'NO VALIDATION JUST YET')
        self.assertEqual(land.area, 100.50)
        self.assertEqual(land.price, 10000000.50)

    def test_put_land__not_found(self):
        response = self.testapp.put('/api/lands/xxx', status=404)
        self.assertEqual(response.status_int, 404)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(json.loads(response.normal_body), 'Error 404 Not Found')


class TestLandDeleteHandler(BaseTestHandler):

    def test_delete_land(self):
        land = Land(
            name = 'Wonderland',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
            area = 100.50,
            price = 10000000.50,
        )
        land.put()

        response = self.testapp.delete('/api/lands/%s' % str(land.key()))
        self.assertEqual(response.status_int, 204)
        self.assertEqual(response.content_type, None)
        self.assertEqual(response.normal_body, '')

        land = Land.get(land.key())
        self.assertEqual(land, None)

    def test_delete_land__not_found(self):
        response = self.testapp.delete('/api/lands/xxx', status=404)
        self.assertEqual(response.status_int, 404)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(json.loads(response.normal_body), 'Error 404 Not Found')