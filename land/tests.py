import unittest
import webapp2
import webtest

#from google.appengine.ext import testbed

from .handlers import ListOrCreateLandHandler, InstanceLandHandler


class AppTest(unittest.TestCase):

    def setUp(self):
        # Create a WSGI application.
        app = webapp2.WSGIApplication([
            ('/api/lands/?', ListOrCreateLandHandler),
            ('/api/lands/([\w-]*)/?', InstanceLandHandler),

            #        ('/.*', )
        ],
            debug=True)

        self.testapp = webtest.TestApp(app)

    def testListOrCreateLandHandler(self):
        print 'YO'
        response = self.testapp.get('/api/lands')
        print 'Yes'
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.normal_body, [])
        self.assertEqual(response.content_type, 'application/json')

#class SimpleTest(unittest.TestCase):
#    def testAdd(self):
#        self.assertEqual(1+2, 3)
#        self.assertEqual(3, 0)


if __name__ == '__main__':
    unittest.main()