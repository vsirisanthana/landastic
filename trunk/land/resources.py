class Resource:

    def get(self):
        raise NotImplementedError

    def put(self):
        raise NotImplementedError


class ModelResource(Resource):

    def __init__(self, model):
        self.model = model

    def get(self, key):
        return self.model.get(key)

    def put(self):
        self.model
