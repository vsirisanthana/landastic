import webapp2

from .handlers import LandInstanceHandler, LandListOrCreateHandler, LandPriceListOrCreateHandler, AppHandler, TemplateHandler


app = webapp2.WSGIApplication([
        ('/api/lands/?', LandListOrCreateHandler),
        ('/api/lands/([\w-]*)/?', LandInstanceHandler),
        ('/api/lands/([\w-]*)/prices/?', LandPriceListOrCreateHandler),
        ('/templates/(.*)/?', TemplateHandler),
        ('/.*', AppHandler),
    ],
    debug=True)