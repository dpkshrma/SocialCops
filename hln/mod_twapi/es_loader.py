"""Module to load twitter stream data into ES index"""
import json
import config
import hln.mod_twapi.mappings as maps
import hln.mod_twapi.doc_templates as dt
from hln.mod_twapi.twapi_handler import Scraper
from elasticsearch import Elasticsearch, helpers

def index():
	"""Indexes twitter stream data in ES
	
	Loads twitter stream data using Scraper class from
	twapi_handler module, extracts relevant information as ES docs and 
	bulk indexes the docs in ES index

	Returns None
	"""
	sc = Scraper()
	bulk_size = 1000

	es = Elasticsearch()

	print("Indexing cleaned documents in ES...")

	if not es.indices.exists(index=config.es_index_name):
		m = {'mappings': maps.doc_mappings}
		es.indices.create(index=config.es_index_name, body=json.dumps(m))

	# indexing leads and reporters
	# bulk actions
	actions = []
	data = {
		"lead": sc.leads,
		"reporter": sc.reporters
	}

	for doc_type in data:
		for doc in data[doc_type]:
			action = {
				"_index": config.es_index_name,
				"_type": doc_type,
				"_id": doc['id'],
				"_source": doc
			}
			actions.append(action)

	num_bulks = len(actions)/bulk_size

	i=0
	while i<=num_bulks:
		# start and end index of docs to be indexed
		start = i*bulk_size
		end = (i+1)*bulk_size

		# perform bulk operations
		helpers.bulk(es, actions[start:end])
		i += 1

	# refresh index to reflect changes
	es.indices.refresh(index=config.es_index_name)