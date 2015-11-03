
def get_leads_query(args):
	"""Forms leads query on basis of filters(categories and entities),
		and using relevance score boost on entities match in search text
	
	Args:
	    args (dict): search query dictionary containing search text,
	    	categories, and entities
	
	Returns:
	    dict: ES query
	"""
	search_filters = []

	if len(args['search_entities'])!=0:
		entities_filter = get_entities_filter(args['search_entities'])
		search_filters.insert(0, entities_filter)

	if len(args['search_categories'])!=0:
		categories_filter = get_categories_filter(args['search_categories'])
		search_filters.insert(0, categories_filter)

	if len(search_filters)==0:
		leads_query = get_leads_boost_query(args)
	else:
		leads_query = {
    	    "filtered": {
				"query": get_leads_boost_query(args),
				"filter": {
			    	"bool": {
			        	"should": search_filters
				    }
				}
			}
		}
	return leads_query

def get_entities_filter(search_entities):
	"""Forms filter dictionary for search_entities
	
	Args:
	    search_entities (string): entities in search text
	
	Returns:
	    dict: ES filter query
	"""
	return {
		"nested": {
			"path": "data.entities",
				"filter":{
					"bool":{
						"should": [
						{
							"terms": {
								"data.entities.screen_name": search_entities
							}
						},
						{
							"terms": {
								"data.entities.name": search_entities
							}
						}
					]
				}
			}
	    }
	}

def get_categories_filter(search_categories):
	"""Forms categories filter
	
	Args:
	    search_categories (string): categories in search text
	
	Returns:
	    dict: ES filter query
	"""
	return {
		"terms": {
			"categories": search_categories
		}
	}

def get_leads_boost_query(args):
	"""Forms leads boost query on basis of entities
		in search text
	
	Args:
	    args (dict): contains search text, categories, entities
	
	Returns:
	    dict: ES query
	"""
	return {
	    "nested": {
	       "path": "data",
	       "query": {
	            "bool": {
	               "should": [
						{
						   "match": {
						      "data.text":{
						          "query":args['search_text']
						      }
						   }
						},
						{
						    "nested": {
						       "path": "data.entities",
						       "query": {
						           "match": {
						              "data.entities.name":{
						                  "query": args['search_text'].replace('@',''),
						                  "boost": 2
						              }
						           }
						       }
						    }
						}
	               ]
	           }
	       }
	    }
	}