from google.appengine.ext import db


class Land(db.Model):
    name = db.StringProperty()
    location = db.GeoPtProperty()
    features = db.TextProperty()

    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
