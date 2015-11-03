"""Main run script to start server and load data in ES"""
import argparse
import hln.mod_twapi.es_loader as es_loader
from hln import app

def init():
	"""Loads ES with tweets and starts server

	Loads ES with the fetched tweet stream,
	and start the flask application server
	"""
	es_load()
	start_server()

def es_load():
	"""Loads ES with tweets

	Fetches data from twitter stream and
	indexes parsed data in ES index
	"""
	es_loader.index()

def start_server():
	"""Start the server

	Starts the Flask application server on
	localhost, port 8080
	"""
	app.run(host='127.0.0.1', port=8080, debug=True)

def create_arg_parser():
	"""Creates argument parser
	
	Returns:
	    argparse.ArgumentParser: Parser to fetch arguments from terminal
	"""
	parser = argparse.ArgumentParser(description="Welcome to Homeless Network Server! (run to start server)", prog="HomelessNet")

	parser.add_argument('--init', dest='run_init', action='store_true', help="Fetch tweets, load ES index, start the server")
	parser.add_argument('--esload', dest='run_es_load', action='store_true', help="Fetch tweets from twitter api and load ES index")

	return parser

if __name__ == '__main__':
	parser = create_arg_parser()
	args = parser.parse_args()
	if args.run_init:
		init()
	elif args.run_es_load:
		es_load()
	else:
		start_server()
