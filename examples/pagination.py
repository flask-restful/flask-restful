from flask.ext.restful.paging import retreive_next_page
from flask import Flask
from flask_restful import Api, LinkedResource, Embed
from flask_restful.declarative import output, Verb
from flask_restful.fields import String


app = Flask(__name__)
api = Api(app, api_explorer=True)

def fetch_houses(filters, bookmark, page_size):
    """
    Fake callback that should return the object filtered by filters, starting from bookmark and with at most page_size elements
    :param filters:
    :param bookmark:
    :param page_size:
    :return: the tuple (result, filter, approx_result_size)
    """
    if not bookmark:
        bookmark = 0
    print "Fetch houses bookmark = %i, page_size = %i" % (bookmark, page_size)

    # Here you should put you logic retrieving the objects and returning with them
    # the last element id and approximative size of the set
    stop = bookmark + page_size
    return [Embed(House, {"HOUSE_ID": i}) for i in range(bookmark, stop)], stop, 10000


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

        CRYPTO_SEED = 'DEADBEEFCAFEBABE0123456789abcdef'.decode('hex')  # this is used to encrypt the bookmark, use something derived from your accounts for example.
        result, f, approx_result_size = retreive_next_page('0123456789abcdef0123456789abcdef', CRYPTO_SEED, {}, fetch_houses)
        return output(Houses=houses), filter, approx_result_size


api.add_root(Town)

if __name__ == '__main__':
    app.run(debug=True)
