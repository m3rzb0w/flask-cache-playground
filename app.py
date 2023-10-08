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

class Ping(Resource):
    def get(self):
        current_datetime = datetime.now()
        return {"ping" : f"{current_datetime}"}, 200

api.add_resource(Catfact, '/catfact')
api.add_resource(Ping, '/ping')

if __name__ == '__main__':
    app.run(debug=True)