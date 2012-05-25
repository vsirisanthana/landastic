import webapp2

from .handlers import LandInstanceHandler, LandListOrCreateHandler, MainHandler, TemplateHandler


app = webapp2.WSGIApplication([
        ('/api/lands/?', LandListOrCreateHandler),
        ('/api/lands/([\w-]*)/?', LandInstanceHandler),
        ('/templates/(.*)/?', TemplateHandler),
        ('/', MainHandler),
    ],
    debug=True)