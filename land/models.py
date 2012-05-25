from google.appengine.ext import db


class BaseModel(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    created_by = db.UserProperty()
    last_modified = db.DateTimeProperty(auto_now=True)
    last_modified_by = db.UserProperty()


class Land(BaseModel):
    name = db.StringProperty()
    location = db.GeoPtProperty()
    features = db.TextProperty()

