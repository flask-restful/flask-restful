
from flask import Flask
from flask_restful import Api, LinkedResource, Embed, ResourceLink
from flask_restful.declarative import parameters, output, Verb, link
from flask_restful.fields import String

app = Flask(__name__)
api = Api(app, api_explorer=True)


class House(LinkedResource):
    """
        This is one house
    """
    _self = '/town/house/<HOUSE_ID>'

    @Verb(output_fields=output(message=String))
    def get(self, HOUSE_ID=None):
        return output(message="This is the house called : [%s]" % HOUSE_ID)


class Town(LinkedResource):
    """
        This is a sample of a town linking composed of a list of houses
    """
    _self = '/town'

    @Verb(output_fields=output(Houses=[House]))  # directly reference the embedded type here
    def get(self):
        houses = [Embed(House, {"HOUSE_ID": i}) for i in range(100)]

        return output(Houses=houses)  # This manually inserts the embedded instance in the response


api.add_root(Town)

if __name__ == '__main__':
    app.run(debug=True)
