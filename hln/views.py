"""Contains Classes for different View Routes

Attributes:
    url_rules (list): contains url rule objects, for add_url_rules() function
"""
import flask, flask.views
import functools
import config
import json
from nltk import word_tokenize
from nltk.corpus import stopwords
from hln.user import User
from hln import app
from hln import es

def login_required(method):
	"""Checks Login status of user

	Annotation method to check authorise url route.
	Wraps a function using functools module

	Args:
	    method (class bound method): get/post methods of different a url route class
	
	Returns:
	    function: wrapper function
	"""
	@functools.wraps(method)
	def wrapper(*args, **kwargs):
		"""Wrapper function to check user login

		Redirects user to /login/ url if user not in session,
		else execute wrapped get/post method

		Args:
		    *args: positional arguments
		    **kwargs: keyword arguments
		
		Returns:
		    method/redirect output: wrapped method output or 
		"""
		if 'username' in flask.session:
			return method(*args, **kwargs)
		else:
			flask.flash("A login is required")
			return flask.redirect(flask.url_for("login"))
	return wrapper

def add_url_rules(url_rules):
	"""Adds Flask Url Route Rules to Flask app (flask.Flask module)

	Args:
	    url_rules (list): list of url object. Every object must have
	    	required keys - 'url, class, view_name' and can have
	    	optional key - 'methods' ('GET'/'POST')
	Returns:
		None
	"""
	for rule in url_rules:
		if 'methods' not in rule:
			rule['methods'] = ['GET']
		app.add_url_rule(
			rule['url'],
			view_func=rule['class'].as_view(rule['view_name']),
			methods=rule['methods']
		)

class Home(flask.views.MethodView):
	"""Base url route Class"""
	@login_required
	def get(self):
		"""renders main dashboard
		
		Returns:
			None
		"""
		return flask.render_template("dashboard.html")

class Login(flask.views.MethodView):
	"""Login url route Class"""
	def get(self):
		""" renders login page when user not in session,
			redirects to home otherwise

		Returns:
			redirect: page redirect
		"""
		if 'username' in flask.session:
			return flask.redirect(flask.url_for('home'))
		else:
			return flask.render_template("login.html")

	def post(self):
		"""Checks for user credentials
		
		Returns:
		    redirect: page redirect
		"""
		cred = {
			'username': flask.request.form['email'],
			'password': flask.request.form['password']
		}
		# @todo : clean and validate cred

		user = User(cred)

		if user.authenticate():
			flask.session['username'] = cred['username']
			return flask.redirect(flask.url_for('home'))
		else:
			flask.flash("User Authentication Failed. Please try again.")

		return self.get()

class Logout(flask.views.MethodView):
	"""Logout url route Class"""
	@login_required
	def get(self):
		"""Clears flask session and redirects to login page
		
		Returns:
		    redirect: page redirect
		"""
		flask.session.pop('username', None)
		return flask.redirect(flask.url_for('login'))

class Leads(flask.views.MethodView):
	"""Leads url route Class"""
	@login_required
	def post(self):
		"""Processes search query string using nltk,
		and fetches latest leads from elasticsearch
		handler (es_handler) module
		
		Returns:
		    string: processed leads docs (relevance boosted and filtered based on query)
		"""
		count = flask.request.form.get('count') or 5
		offset = flask.request.form.get('offset') or 0
		search_query = flask.request.form.get('search_query') or ''
		if len(str(search_query))>0:
			search_query = self.process_query(search_query);
		leads = es.get_latest_leads(search_query, count, offset)
		return json.dumps(leads)

	def process_query(self, search_query):
		"""Removes stopwords, extracts categories(#tags) and entities(@mentions)
		
		Args:
		    search_query (string): search query string
		
		Returns:
		    dict: parsed dictionary containing tokens, categories and entities
		"""
		res = {}
		# remove stopwords
		stop = stopwords.words("english")
		tokens = search_query.split()
		res['tokens'] = [token.lower() for token in tokens if token not in stop]

		# get #hash_tags from search query
		res['categories'] = [hash_tag.lower()[1:] for hash_tag in tokens if hash_tag[0]=="#"]

		# get @mentions from search query
		res['entities'] = [mention.lower()[1:] for mention in tokens if mention[0]=="@"]

		return res

class Reporters(flask.views.MethodView):
	"""Reporters url route Class"""
	@login_required
	def post(self):
		"""Fetches reporter document from ES, based on
			reporter id
		
		Returns:
		    string: reporter document
		"""
		reporter_id = flask.request.form.get('reporter_id') or 0
		reporter = json.dumps(es.get_reporter(reporter_id))
		return reporter

class LeadCount(flask.views.MethodView):
	"""LeadCount url route Class"""
	@login_required
	def post(self):
		"""Fetches lead document count based on bucket aggregations
			if agg_type is None, it fetches total documents count
		
		Returns:
		    string: document counts
		"""
		agg_type = flask.request.form.get('agg_type')
		agg_size = flask.request.form.get('agg_size') or 10
		time_interval = flask.request.form.get('time_interval')
		count_res = json.dumps(es.get_leadcount(agg_type, time_interval, agg_size))
		return count_res

class ReporterCount(flask.views.MethodView):
	"""ReporterCount url route Class"""
	@login_required
	def post(self):
		"""Fetches reporter documents count from ES
		
		Returns:
		    string: reporters count
		"""
		count_res = json.dumps(es.get_reportercount())
		return count_res

url_rules = [
	{'url':'/', 'class':Home, 'view_name':'home'},
	{'url':'/logout/', 'class':Logout, 'view_name':'logout'},
	{'url':'/login/', 'class':Login, 'view_name':'login', 'methods':['GET', 'POST']},
	{'url':'/lead/get/', 'class':Leads, 'view_name':'leads', 'methods':['GET', 'POST']},
	{'url':'/lead/count/get/', 'class':LeadCount, 'view_name':'leadcount', 'methods':['GET', 'POST']},
	{'url':'/reporter/get/', 'class':Reporters, 'view_name':'reporters', 'methods':['GET', 'POST']},
	{'url':'/reporter/count/get/', 'class':ReporterCount, 'view_name':'reportercount', 'methods':['GET', 'POST']}
]

# add url rules to Flask app
add_url_rules(url_rules)