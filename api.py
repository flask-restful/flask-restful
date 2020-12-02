# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 19:57:18 2020

@author: sewer
"""

from flask import Flask, redirect, request
from flask_restful import Resource, Api
from flask_sslify import SSLify
import json
import requests
from OpenSSL import SSL
from app import app

webcrt = "/etc/letsencrypt/live/diet.lidkicker.com/cert.pem"
webkey = "/etc/letsencrypt/live/diet.lidkicker.com/privkey.pem"
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file(webkey)
context.use_certificate_file(webcrt)


# @app.before_request
# def before_request():
#     if not request.is_secure and app.env != "development":
#         url = request.url.replace("http://", "https://", 1)
#         code = 301
#         return redirect(url, code=code)



#sslify = SSLify(app)

api = Api(app)



def get_random_word():
    api_key = "kgx4wey9hz5a1v3vuq3ks9e87v15zzk2xk7khkn5brluofc9r"
    urlbase = "http://api.wordnik.com/v4/words.json/randomWord?api_key=" + api_key

    response = requests.get(urlbase)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        return_word = ""
        for k, v in json_data.items():
            if k == "word":
                return_word = v
        return return_word
    return False


class HelloWorld(Resource):
    def get(self):
        return get_random_word()

#
# api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    context = (webcrt, webkey)
    app.run(host='0.0.0.0', port=7475, ssl_context=context, debug=True)

