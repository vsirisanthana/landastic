import webapp2

from .handlers import LandInstanceHandler, LandListOrCreateHandler, AppHandler, TemplateHandler


app = webapp2.WSGIApplication([
        ('/api/lands/?', LandListOrCreateHandler),
        ('/api/lands/([\w-]*)/?', LandInstanceHandler),
        ('/templates/(.*)/?', TemplateHandler),
        ('/', AppHandler),
    ],
    debug=True)