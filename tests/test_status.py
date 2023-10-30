import uuid
import unittest
from flask import Flask
import flask_restful
from flask_restful.utils import status

def status_wrapper(status_code):
    class DummyHandler(flask_restful.Resource):
        def get(self):
            return {}, status_code
        
    DummyHandler.__name__ =  str(uuid.uuid4())
    
    return DummyHandler

class StatusTestCases(unittest.TestCase):
    def test_success_statuses(self):
        is_success = all([ True if (value >= 200 and value <= 299) else False for name, value in vars(status).items() if name.startswith("STATUS_2")])
        self.assertTrue(is_success)

    def test_information_statuses(self):
        is_info_status = all([ True if (value >= 100 and value <= 199) else False for name, value in vars(status).items() if name.startswith("STATUS_1")])
        self.assertTrue(is_info_status)
    def test_redirect_statuses(self):
        is_redirect_statuses = all([ True if (value >= 300 and value <= 399) else False for name, value in vars(status).items() if name.startswith("STATUS_3")])
        self.assertTrue(is_redirect_statuses)
    
    def test_client_error_statuses(self):
        is_client_error = all([ True if (value >= 400 and value <= 499) else False for name, value in vars(status).items() if name.startswith("STATUS_4")])
        self.assertTrue(is_client_error)
    
    def test_client_server_statuses(self):
        is_server_error = all([ True if (value >= 500 and value <= 599) else False for name, value in vars(status).items() if name.startswith("STATUS_5")])
        self.assertTrue(is_server_error)

    def test_common_status_codes(self):
        flask_app =  Flask(__name__)
        api = flask_restful.Api(flask_app)
        
        
        api.add_resource(status_wrapper(status.STATUS_200_OK), '/ok')
        api.add_resource(status_wrapper(status.STATUS_201_CREATED), '/created')
        api.add_resource(status_wrapper(status.STATUS_204_NO_CONTENT), '/no-content')
        api.add_resource(status_wrapper(status.STATUS_400_BAD_REQUEST), '/bad-req')
        api.add_resource(status_wrapper(status.STATUS_401_UNAUTHORIZED), '/unauthorized')
        api.add_resource(status_wrapper(status.STATUS_500_INTERNAL_SERVER_ERROR), '/server-error')



        with flask_app.test_client() as client:
            res = client.get('/ok')
            self.assertEqual(res.status_code, 200)
            
            res = client.get('/created')
            self.assertEqual(res.status_code, 201)

            res = client.get('/no-content')
            self.assertEqual(res.status_code, 204)

            res = client.get('/bad-req')
            self.assertEqual(res.status_code, 400)
            
            res = client.get('/unauthorized')
            self.assertEqual(res.status_code, 401)

            res = client.get('/server-error')
            self.assertEqual(res.status_code, 500)

if __name__ == '__main__':
    unittest.main()