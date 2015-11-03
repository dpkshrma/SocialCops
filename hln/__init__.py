"""Creates Flask app and includes view url route classes

Attributes:
    app (flask.Flask object): Flask application object
    es (ES_Handler object): Elasticsearch Handler object
"""
import flask
from hln.es_handler import ES_Handler
import config

app = flask.Flask(__name__, static_url_path='')
app.secret_key = config.secret_key
es = ES_Handler()

# import views
import hln.views