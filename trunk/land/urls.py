import webapp2

from .handlers import LandInstanceHandler, LandListOrCreateHandler


app = webapp2.WSGIApplication([
        ('/api/lands/?', LandListOrCreateHandler),
        ('/api/lands/([\w-]*)/?', LandInstanceHandler),

#        ('/.*', )
    ],
    debug=True)