import datetime
import logging
import json
import unittest
import webtest

from google.appengine.ext import testbed

from ..models import Land, Price
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

    def test_create_land__form_urlencoded(self):
        response = self.testapp.post('/api/lands', {
            'name': 'Wonderland',
            'description': 'Wonderland is located underground, and Alice reaches it by travelling down a rabbit hole.',
            'location': '18.769937,99.003156',
            'features': 'NO VALIDATION YET',
            'area': 100.50,
            'price': 10000000.50,
        })
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.content_type, 'application/json')

        response_land = json.loads(response.normal_body)
        self.assertEqual(response_land['name'], 'Wonderland')
        self.assertEqual(response_land['description'], 'Wonderland is located underground, '
                                                       'and Alice reaches it by travelling down a rabbit hole.')
        self.assertEqual(response_land['location'], '18.769937,99.003156')
        self.assertEqual(response_land['features'], 'NO VALIDATION YET')
        self.assertEqual(response_land['area'], 100.50)
        self.assertEqual(response_land['price'], 10000000.50)

        land = Land.get(response_land['key'])
        self.assertEqual(land.name, 'Wonderland')
        self.assertEqual(land.description, 'Wonderland is located underground, '
                                           'and Alice reaches it by travelling down a rabbit hole.')
        self.assertEqual(land.location, '18.769937,99.003156')
        self.assertEqual(land.features, 'NO VALIDATION YET')
        self.assertEqual(land.area, 100.50)
        self.assertEqual(land.price, 10000000.50)

    def test_create_land(self):
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
        response = self.testapp.post('/api/lands', json.dumps({
            'name': 'Wonderland',
            'location': '18.769937,99.003156',
            'features': 'NO VALIDATION YET',
        }), content_type='application/json')
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

    def test_put_land__form_urlencoded(self):
        land = Land(
            name = 'Wonderland',
            description = 'Wonderland is located underground, and Alice reaches it by travelling down a rabbit hole.',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
            area = 100.50,
            price = 10000000.50,
        )
        land.put()

        response = self.testapp.put('/api/lands/%s' % str(land.key()), {
            'name': 'Neverland',
            'description': 'The dwelling place of Peter Pan, Tinker Bell, the Lost Boys, and others.',
            'location': '20.769937,100.003156',
            'features': 'NO VALIDATION JUST YET',
            'area': 200.50,
            'price': 20000000.50,
        })
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_land = json.loads(response.normal_body)
        self.assertEqual(response_land['name'], 'Neverland')
        self.assertEqual(response_land['description'], 'The dwelling place of Peter Pan, Tinker Bell, '
                                                       'the Lost Boys, and others.')
        self.assertEqual(response_land['location'], '20.769937,100.003156')
        self.assertEqual(response_land['features'], 'NO VALIDATION JUST YET')
        self.assertEqual(response_land['area'], 200.50)
        self.assertEqual(response_land['price'], 20000000.50)

        land = Land.get(land.key())
        self.assertEqual(land.name, 'Neverland')
        self.assertEqual(land.description, 'The dwelling place of Peter Pan, Tinker Bell, '
                                           'the Lost Boys, and others.')
        self.assertEqual(land.location, '20.769937,100.003156')
        self.assertEqual(land.features, 'NO VALIDATION JUST YET')
        self.assertEqual(land.area, 200.50)
        self.assertEqual(land.price, 20000000.50)

    def test_put_land(self):
        land = Land(
            name = 'Wonderland',
            description = 'Wonderland is located underground, and Alice reaches it by travelling down a rabbit hole.',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
            area = 100.50,
            price = 10000000.50,
        )
        land.put()

        response = self.testapp.put('/api/lands/%s' % str(land.key()), json.dumps({
            'name': 'Neverland',
            'description': 'The dwelling place of Peter Pan, Tinker Bell, the Lost Boys, and others.',
            'location': '20.769937,100.003156',
            'features': 'NO VALIDATION JUST YET',
            'area': 200.50,
            'price': 20000000.50,
        }), content_type='application/json')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_land = json.loads(response.normal_body)
        self.assertEqual(response_land['name'], 'Neverland')
        self.assertEqual(response_land['description'], 'The dwelling place of Peter Pan, Tinker Bell, '
                                                       'the Lost Boys, and others.')
        self.assertEqual(response_land['location'], '20.769937,100.003156')
        self.assertEqual(response_land['features'], 'NO VALIDATION JUST YET')
        self.assertEqual(response_land['area'], 200.50)
        self.assertEqual(response_land['price'], 20000000.50)

        land = Land.get(land.key())
        self.assertEqual(land.name, 'Neverland')
        self.assertEqual(land.description, 'The dwelling place of Peter Pan, Tinker Bell, '
                                           'the Lost Boys, and others.')
        self.assertEqual(land.location, '20.769937,100.003156')
        self.assertEqual(land.features, 'NO VALIDATION JUST YET')
        self.assertEqual(land.area, 200.50)
        self.assertEqual(land.price, 20000000.50)

    def test_put_land__required_fields(self):
        land = Land(
            name = 'Wonderland',
            description = 'Wonderland is located underground, and Alice reaches it by travelling down a rabbit hole.',
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
        }), content_type='application/json')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_land = json.loads(response.normal_body)
        self.assertEqual(response_land['name'], 'Neverland')
        self.assertEqual(response_land['description'], 'Wonderland is located underground, '
                                                       'and Alice reaches it by travelling down a rabbit hole.')
        self.assertEqual(response_land['location'], '20.769937,100.003156')
        self.assertEqual(response_land['features'], 'NO VALIDATION JUST YET')
        self.assertEqual(response_land['area'], 100.50)
        self.assertEqual(response_land['price'], 10000000.50)

        land = Land.get(land.key())
        self.assertEqual(land.name, 'Neverland')
        self.assertEqual(land.description, 'Wonderland is located underground, '
                                           'and Alice reaches it by travelling down a rabbit hole.')
        self.assertEqual(land.location, '20.769937,100.003156')
        self.assertEqual(land.features, 'NO VALIDATION JUST YET')
        self.assertEqual(land.area, 100.50)
        self.assertEqual(land.price, 10000000.50)

    def test_put_land__empty_optional_fields(self):
        land = Land(
            name = 'Wonderland',
            description = 'Wonderland is located underground, and Alice reaches it by travelling down a rabbit hole.',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
            area = 100.50,
            price = 10000000.50,
        )
        land.put()

        response = self.testapp.put('/api/lands/%s' % str(land.key()), json.dumps({
            'name': 'Neverland',
            'description': '',
            'location': '20.769937,100.003156',
            'features': 'NO VALIDATION JUST YET',
            'area': None,
            'price': None,
        }), content_type='application/json')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_land = json.loads(response.normal_body)
        self.assertEqual(response_land['name'], 'Neverland')
        self.assertEqual(response_land['description'], '')
        self.assertEqual(response_land['location'], '20.769937,100.003156')
        self.assertEqual(response_land['features'], 'NO VALIDATION JUST YET')
        self.assertEqual(response_land['area'], None)
        self.assertEqual(response_land['price'], None)

        land = Land.get(land.key())
        self.assertEqual(land.name, 'Neverland')
        self.assertEqual(land.description, '')
        self.assertEqual(land.location, '20.769937,100.003156')
        self.assertEqual(land.features, 'NO VALIDATION JUST YET')
        self.assertEqual(land.area, None)
        self.assertEqual(land.price, None)

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


class TestLandPriceListHandler(BaseTestHandler):

    def test_list_empty(self):
        land = Land(
            name = 'Wonderland',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
        )
        land.put()

        response = self.testapp.get('/api/lands/%s/prices' % land.key())
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(json.loads(response.normal_body), [])

    def test_list_one_price(self):
        land = Land(
            name = 'Wonderland',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
        )
        land.put()

        price = Price(
            parent = land,
            type = 'ask',
            value = 10000000.00,
            date = datetime.datetime(2012, 8, 25, 1, 1, 1)
        )
        price.put()

        response = self.testapp.get('/api/lands/%s/prices' % land.key())
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_prices = json.loads(response.normal_body)
        self.assertEqual(len(response_prices), 1)

        response_price = response_prices[0]
        self.assertEqual(response_price['key'], str(price.key()))
        self.assertEqual(response_price['type'], 'ask')
        self.assertEqual(response_price['value'], 10000000.00)
        self.assertEqual(response_price['date'], str(datetime.datetime(2012, 8, 25, 1, 1, 1)))

    def test_list_multiple_prices(self):
        land = Land(
            name = 'Wonderland',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
        )
        land.put()

        price0 = Price(
            parent = land,
            type = 'ask',
            value = 10000000.00,
            date = datetime.datetime(2012, 8, 25, 1, 1, 1)
        )
        price0.put()

        price1 = Price(
            parent = land,
            type = 'bid',
            value = 9000000.00,
            date = datetime.datetime(2012, 8, 30, 2, 2, 2)
        )
        price1.put()

        price2 = Price(
            parent = land,
            type = 'market',
            value = 9500000.00,
            date = datetime.datetime(2012, 8, 28, 3, 3, 3)
        )
        price2.put()

        response = self.testapp.get('/api/lands/%s/prices' % land.key())
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_prices = json.loads(response.normal_body)
        self.assertEqual(len(response_prices), 3)

        response_price0 = response_prices[0]
        self.assertEqual(response_price0['key'], str(price1.key()))
        self.assertEqual(response_price0['type'], 'bid')
        self.assertEqual(response_price0['value'], 9000000.00)
        self.assertEqual(response_price0['date'], str(datetime.datetime(2012, 8, 30, 2, 2, 2)))

        response_price1 = response_prices[1]
        self.assertEqual(response_price1['key'], str(price2.key()))
        self.assertEqual(response_price1['type'], 'market')
        self.assertEqual(response_price1['value'], 9500000.00)
        self.assertEqual(response_price1['date'], str(datetime.datetime(2012, 8, 28, 3, 3, 3)))

        response_price2 = response_prices[2]
        self.assertEqual(response_price2['key'], str(price0.key()))
        self.assertEqual(response_price2['type'], 'ask')
        self.assertEqual(response_price2['value'], 10000000.00)
        self.assertEqual(response_price2['date'], str(datetime.datetime(2012, 8, 25, 1, 1, 1)))

    def test_list_multiple_lands_multiple_prices(self):
        land0 = Land(
            name = 'Wonderland',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
        )
        land0.put()

        land1 = Land(
            name = 'Dreamland',
            location = '5.797771,-15.967979',
            features = 'NO VALIDATION AS YET',
        )
        land1.put()

        price0 = Price(
            parent = land0,
            type = 'ask',
            value = 10000000.00,
            date = datetime.datetime(2012, 8, 25, 1, 1, 1)
        )
        price0.put()

        price1 = Price(
            parent = land0,
            type = 'bid',
            value = 9000000.00,
            date = datetime.datetime(2012, 8, 30, 2, 2, 2)
        )
        price1.put()

        price2 = Price(
            parent = land0,
            type = 'market',
            value = 9500000.00,
            date = datetime.datetime(2012, 8, 28, 3, 3, 3)
        )
        price2.put()

        price3 = Price(
            parent = land1,
            type = 'ask',
            value = 500000.00,
            date = datetime.datetime(2012, 8, 27)
        )
        price3.put()

        price4 = Price(
            parent = land1,
            type = 'bid',
            value = 450000.00,
            date = datetime.datetime(2012, 8, 26)
        )
        price4.put()

        response = self.testapp.get('/api/lands/%s/prices' % land0.key())
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_prices = json.loads(response.normal_body)
        self.assertEqual(len(response_prices), 3)

        response_price0 = response_prices[0]
        self.assertEqual(response_price0['key'], str(price1.key()))
        self.assertEqual(response_price0['type'], 'bid')
        self.assertEqual(response_price0['value'], 9000000.00)
        self.assertEqual(response_price0['date'], str(datetime.datetime(2012, 8, 30, 2, 2, 2)))

        response_price1 = response_prices[1]
        self.assertEqual(response_price1['key'], str(price2.key()))
        self.assertEqual(response_price1['type'], 'market')
        self.assertEqual(response_price1['value'], 9500000.00)
        self.assertEqual(response_price1['date'], str(datetime.datetime(2012, 8, 28, 3, 3, 3)))

        response_price2 = response_prices[2]
        self.assertEqual(response_price2['key'], str(price0.key()))
        self.assertEqual(response_price2['type'], 'ask')
        self.assertEqual(response_price2['value'], 10000000.00)
        self.assertEqual(response_price2['date'], str(datetime.datetime(2012, 8, 25, 1, 1, 1)))

        response = self.testapp.get('/api/lands/%s/prices' % land1.key())
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'application/json')

        response_prices = json.loads(response.normal_body)
        self.assertEqual(len(response_prices), 2)

        response_price0 = response_prices[0]
        self.assertEqual(response_price0['key'], str(price3.key()))
        self.assertEqual(response_price0['type'], 'ask')
        self.assertEqual(response_price0['value'], 500000.00)
        self.assertEqual(response_price0['date'], str(datetime.datetime(2012, 8, 27)))

        response_price1 = response_prices[1]
        self.assertEqual(response_price1['key'], str(price4.key()))
        self.assertEqual(response_price1['type'], 'bid')
        self.assertEqual(response_price1['value'], 450000.00)
        self.assertEqual(response_price1['date'], str(datetime.datetime(2012, 8, 26)))

    def test_list_prices__land_not_found(self):
        response = self.testapp.get('/api/lands/xxx/prices', status=404)
        self.assertEqual(response.status_int, 404)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(json.loads(response.normal_body), 'Error 404 Not Found')


class TestLandPriceCreateHandler(BaseTestHandler):

#    def test_create_land__form_urlencoded(self):
#
#
#        response = self.testapp.post('/api/lands', {
#            'name': 'Wonderland',
#            'description': 'Wonderland is located underground, and Alice reaches it by travelling down a rabbit hole.',
#            'location': '18.769937,99.003156',
#            'features': 'NO VALIDATION YET',
#            'area': 100.50,
#            'price': 10000000.50,
#        })
#        self.assertEqual(response.status_int, 201)
#        self.assertEqual(response.content_type, 'application/json')
#
#        response_land = json.loads(response.normal_body)
#        self.assertEqual(response_land['name'], 'Wonderland')
#        self.assertEqual(response_land['description'], 'Wonderland is located underground, '
#                                                       'and Alice reaches it by travelling down a rabbit hole.')
#        self.assertEqual(response_land['location'], '18.769937,99.003156')
#        self.assertEqual(response_land['features'], 'NO VALIDATION YET')
#        self.assertEqual(response_land['area'], 100.50)
#        self.assertEqual(response_land['price'], 10000000.50)
#
#        land = Land.get(response_land['key'])
#        self.assertEqual(land.name, 'Wonderland')
#        self.assertEqual(land.description, 'Wonderland is located underground, '
#                                           'and Alice reaches it by travelling down a rabbit hole.')
#        self.assertEqual(land.location, '18.769937,99.003156')
#        self.assertEqual(land.features, 'NO VALIDATION YET')
#        self.assertEqual(land.area, 100.50)
#        self.assertEqual(land.price, 10000000.50)

    def test_create_land_price(self):
        land = Land(
            name = 'Wonderland',
            location = '18.769937,99.003156',
            features = 'NO VALIDATION YET',
        )
        land.put()

        response = self.testapp.post('/api/lands/%s/prices' % land.key(), json.dumps({
            'type': 'ask',
            'value': 500000.00,
            'date': str(datetime.datetime(2012, 8, 25)),
        }), content_type='application/json')
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.content_type, 'application/json')

        response_price = json.loads(response.normal_body)
        self.assertEqual(response_price['type'], 'ask')
        self.assertEqual(response_price['value'], 500000.00)
        self.assertEqual(response_price['date'], str(datetime.datetime(2012, 8, 25)))

        price = Price.get(response_price['key'])
        self.assertEqual(price.type, 'ask')
        self.assertEqual(price.value, 500000.00)
        self.assertEqual(price.date, datetime.datetime(2012, 8, 25))
        self.assertEqual(price.parent().key(), land.key())
        self.assertEqual(price.parent_key(), land.key())

#    def test_create_land__required_fields(self):
#        response = self.testapp.post('/api/lands', json.dumps({
#            'name': 'Wonderland',
#            'location': '18.769937,99.003156',
#            'features': 'NO VALIDATION YET',
#            }), content_type='application/json')
#        self.assertEqual(response.status_int, 201)
#        self.assertEqual(response.content_type, 'application/json')
#
#        response_land = json.loads(response.normal_body)
#        self.assertEqual(response_land['name'], 'Wonderland')
#        self.assertEqual(response_land['location'], '18.769937,99.003156')
#        self.assertEqual(response_land['features'], 'NO VALIDATION YET')
#
#        land = Land.get(response_land['key'])
#        self.assertEqual(land.name, 'Wonderland')
#        self.assertEqual(land.location, '18.769937,99.003156')
#        self.assertEqual(land.features, 'NO VALIDATION YET')