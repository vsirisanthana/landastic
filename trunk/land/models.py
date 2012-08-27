from google.appengine.ext import db


class BaseModel(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    created_by = db.UserProperty(auto_current_user_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    last_modified_by = db.UserProperty(auto_current_user=True)


class Land(BaseModel):
    name = db.StringProperty()
    description = db.TextProperty()
    location = db.GeoPtProperty()
    features = db.TextProperty()
    area = db.FloatProperty()
    price = db.FloatProperty()


class Price(BaseModel):
    type = db.StringProperty(required=True)
    value = db.FloatProperty(required=True)
    date = db.DateTimeProperty(required=True)