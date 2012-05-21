from google.appengine.ext import db


class Land(db.Model):
    name = db.StringProperty()
    location = db.GeoPtProperty()
    features = db.TextProperty()