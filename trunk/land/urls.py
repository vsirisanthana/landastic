import webapp2

from .handlers import InstanceLandHandler, ListOrCreateLandHandler


app = webapp2.WSGIApplication([
        ('/lands/?', ListOrCreateLandHandler),
        ('/lands/([\w-]*)/?', InstanceLandHandler),
    ],
    debug=True)