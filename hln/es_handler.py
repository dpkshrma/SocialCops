"""Elasticsearch handler"""
from elasticsearch import Elasticsearch as ES
from datetime import datetime, timedelta
import json
import config
import hln.es_queries as esq

class ES_Handler():
	"""ES_Handler Class"""
	def __init__(self):
		"""creates elasticsearch.Elasticsearch object(es)"""
		self.es = ES()

	def get_latest_leads(self, search_query='', count=5, offset=0):
		"""Retrieves latest lead docs with reporter information
		
		Args:
		    search_query (str, optional): search query text
		    count (int, optional): number of lead docs
		    offset (int, optional): lead docs offset
		
		Returns:
		    dict: ES query result
		"""
		leads = self.get_leads(search_query, count, offset)

		# store reporter details for every lead ( @todo : use cache(redis/memcache?) )
		for lead in leads["hits"]["hits"]:
			reporter_id = lead['_source']["reporter_id"]
			lead['_source']['reporter'] = self.get_reporter(reporter_id)["_source"]
		return leads

	def get_leads(self, search_query='', count=5, offset=0):
		"""Retrieves latest lead docs
		
		Args:
		    search_query (str, optional): search query text
		    count (int, optional): number of lead docs
		    offset (int, optional): lead docs offset
		
		Returns:
		    dict: ES query result
		"""
		if len(search_query):
			search_text = ' '.join(search_query['tokens'])
			args = {
				'search_text': search_text,
				'search_categories': search_query['categories'],
				'search_entities': search_query['entities']
			}
			q = esq.get_leads_query(args)
		else:
			q = {
				"match_all":{}
			}

		query = {
			"from":int(offset)*int(count),
			"size":count,
			"query": q
		}
		res = self.es.search(index=config.es_index_name, doc_type='lead', body=query, ignore=[400, 404])
		return res

	def get_reporter(self, reporter_id=None):
		"""Retrieves reporter by id
		
		Args:
		    reporter_id (int, required): reporter id
		
		Returns:
		    dict: ES query result
		"""
		if reporter_id:
			return(self.es.get(index=config.es_index_name, doc_type='reporter', id=str(reporter_id), ignore=[400, 404]))

	def get_doctype_count(self, doc_type="lead"):
		"""Fetches ES doc_type count
		
		Args:
		    doc_type (str, optional): doc_type
		
		Returns:
		    dict: ES query result
		"""
		count = self.es.count(index=config.es_index_name, doc_type=doc_type);
		return count

	def get_reportercount(self):
		"""Fetches reporter docs count
		
		Returns:
		    dict: ES query result
		"""
		count = self.get_doctype_count(doc_type='reporter')
		return count

	def get_leadcount(self, agg_type, time_interval='week', size=10):
		"""Fetches lead docs counts grouped by aggregation type
		
		Args:
		    agg_type (string): aggregation type
		    time_interval (str, optional): date histogram time interval
		    size (int, optional): aggregation buckets counts
		
		Returns:
		    dict: ES query result - lead count grouped by aggregation type
		"""
		if agg_type is None:
			return self.get_doctype_count(doc_type='lead')

		agg = {}
		q = {
			"match_all": {}
		}

		if agg_type == "reporter":
			agg = {
				"count_by_reporter":{
					"terms":{
						"field":"reporter_id",
						"size": size
					}
				}
			}
		elif agg_type == "category":
			agg = {
				"count_by_category":{
					"terms":{
						"field":"categories",
						"size": size,
						"order": {"_count": "desc"}
					}
				}
			}
		elif agg_type == "date":
			agg = {
				"count_by_date":{
					"date_histogram":{
						"field":"created_at",
						"interval": time_interval
					}
				}
			}
			# no size option in date_histogram
			if time_interval == "day":
				di = int(size)
			elif time_interval == "week":
				di = int(float(size)*7)
			elif time_interval == "month":
				di = int(float(size)*30)
			d = (datetime.utcnow() - timedelta(days=di)).strftime("%Y/%m/%d %I:%M:%S")
			q = {
				"filtered":{
					"query":{
						"match_all": {}
					},
					"filter": {
						"range": {
							"created_at": {
								"gte": d
							}
						}
					}
				}
			}

		query = {
			"size": 0,
			"query": q,
			"aggs": agg
		}
		res = self.es.search(index="homeless_net", doc_type='lead', body=query, ignore=[400, 404], _source=False)

		# store reporter names for bucket keys
		if agg_type == "reporter":
			buckets = res['aggregations']['count_by_reporter']['buckets']
			for i, reporter in enumerate(buckets):
				reporter_id = reporter['key']
				reporter_name = self.get_reporter(reporter_id)["_source"]["name"]
				buckets[i]['key'] = reporter_name

		return res