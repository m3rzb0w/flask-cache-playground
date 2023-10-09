from flask import Flask, request
from flask_restful import Resource, Api
from datetime import datetime
from json import loads, dumps
import requests
from flask_caching import Cache


config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config.from_mapping(config)
api = Api(app, catch_all_404s=True, prefix="/api")
cache = Cache(app)


class Catfact(Resource):
    CAT_FACT_URL = "https://catfact.ninja/fact"
    @cache.cached(timeout=5) 
    def get(self):
        try:
            response = self.fetch_cat_fact()
            return response, 200
        except requests.exceptions.RequestException as e:
            return {"error": f"Fetching cat fact - {e}"}, 404

    def fetch_cat_fact(self):
        headers = {}
        payload = {}
        response = requests.get(self.CAT_FACT_URL, headers=headers, data=payload)
        response.raise_for_status()
        return loads(response.text)

class Name(Resource):
    NAME_API_URL = "https://api.genderize.io?name="
    NAME_WHITELIST = {"erlich" : True, "richard" : True}
    def get(self, name):
        if self.NAME_WHITELIST.get(name):
            name_cache = cache.get(f"name_{name}")
            if name_cache is None:
                try:
                    response = self.fetch_name(name)
                    cache.set(f"name_{name}", response, timeout=self.get_cache_timeout())
                    return response, 200
                except requests.exceptions.RequestException as e:
                    return {"error": f"Fetching name - {e}"}, 50
            return name_cache, 200
        return {"error": f"Fetching name"}, 404
    
    def fetch_name(self, name):
        url = f"{self.NAME_API_URL}{name}"
        headers = {}
        payload = {}
        response = requests.get(url, headers=headers, data=payload)
        response.raise_for_status()
        return loads(response.text)

    def get_cache_timeout(self):
        return 10

class Ping(Resource):
    def get(self):
        current_datetime = datetime.now()
        return {"ping" : f"{current_datetime}"}, 200

api.add_resource(Catfact, '/catfact')
api.add_resource(Name, '/name/<string:name>')
api.add_resource(Ping, '/ping')

if __name__ == '__main__':
    app.run(debug=True)