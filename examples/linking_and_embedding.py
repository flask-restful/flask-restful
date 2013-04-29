from flask import Flask
from flask_restful import Api, LinkedResource, Embed, ResourceLink
from flask_restful.declarative import parameters, output, Verb, link
from flask_restful.fields import String

app = Flask(__name__)
api = Api(app, api_explorer=True)


class Office(LinkedResource):
    _self = '/town/office/<OFFICE_ID>'

    @Verb(output_fields=output(message=String))
    def get(self, OFFICE_ID=None):
        return output(message="This is the office called [%s]" % OFFICE_ID)


class House(LinkedResource):
    _self = '/town/house/<HOUSE_ID>'

    @Verb(output_fields=output(message=String))
    def get(self, HOUSE_ID=None):
        return output(message="This is the house called : [%s]" % HOUSE_ID)


class Town(LinkedResource):
    _self = '/town'

    @Verb(output_fields=output(Houses=House),
          output_links=link(Offices=Office))
    def get(self):
        return output(Houses=Embed(House, {"HOUSE_ID": "Simpsons"}), Offices=ResourceLink(Office, params={'OFFICE_ID': 'Twilio HQ'}))


api.add_root(Town)

if __name__ == '__main__':
    app.run(debug=True)
