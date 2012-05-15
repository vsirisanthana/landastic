import webapp2

from .handlers import InstanceLandHandler, ListOrCreateLandHandler


app = webapp2.WSGIApplication([
        ('/api/lands/?', ListOrCreateLandHandler),
        ('/api/lands/([\w-]*)/?', InstanceLandHandler),

#        ('/.*', )
    ],
    debug=True)