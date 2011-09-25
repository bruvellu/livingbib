"""
Mendeley Open API Example Client

Copyright (c) 2010, Mendeley Ltd. <copyright@mendeley.com>

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

For details of the Mendeley Open API see http://dev.mendeley.com/

Example usage:

>>> from pprint import pprint
>>> from mendeley_client import MendeleyClient
>>> mendeley = MendeleyClient('<consumer_key>', '<secret_key>')
>>> try:
>>> 	mendeley.load_keys()
>>> except IOError:
>>> 	mendeley.get_required_keys()
>>> 	mendeley.save_keys()
>>> results = mendeley.search('science')
>>> pprint(results['documents'][0])
{u'authors': None,
 u'doi': None,
 u'id': u'8c18bd50-6f07-11df-b8f0-001e688e2dcb',
 u'mendeley_url': u'http://localhost/research//',
 u'publication_outlet': None,
 u'title': None,
 u'year': None}
>>> documents = mendeley.library()
>>> pprint(documents)
{u'current_page': 0,
 u'document_ids': [u'86175', u'86176', u'86174', u'86177'],
 u'items_per_page': 20,
 u'total_pages': 1,
 u'total_results': 4}
>>> details = mendeley.document_details(documents['document_ids'][0])
>>> pprint(details)
{u'authors': [u'Ben Dowling'],
 u'discipline': {u'discipline': u'Computer and Information Science',
                 u'subdiscipline': None},
 u'tags': ['nosql'],
 u'title': u'NoSQL(EU) Write Up',
 u'year': 2010}
"""
from pprint import pprint
import oauth2 as oauth
import pickle
import httplib
import json
import urllib

class OAuthClient(object):
	"""General purpose OAuth client"""
	def __init__(self, consumer_key, consumer_secret, options = {}):
		# Set values based on provided options, or revert to defaults
		self.host = options.get('host', 'www.mendeley.com')
		self.port = options.get('port', 80)
		self.access_token_url = options.get('access_token_url', '/oauth/access_token/')
		self.request_token_url = options.get('access_token_url', '/oauth/request_token/')
		self.authorize_url = options.get('access_token_url', '/oauth/authorize/')

		if self.port == 80: self.authority = self.host
		else: self.authority = "%s:%d" % (self.host, self.port)

		self.consumer = oauth.Consumer(consumer_key, consumer_secret)

	def get(self, path, token=None):
		url = "http://%s%s" % (self.host, path)
		request = oauth.Request.from_consumer_and_token(
			self.consumer,
			token,
			http_method='GET',
			http_url=url,
		)
		return self._send_request(request, token)

	def post(self, path, post_params, token=None):
		url = "http://%s%s" % (self.host, path)
		request = oauth.Request.from_consumer_and_token(
			self.consumer,
			token,
			http_method='POST',
			http_url=url,
			parameters=post_params
		)
		return self._send_request(request, token)
	
	def delete(self, path, token=None):
		url = "http://%s%s" % (self.host, path)
		request = oauth.Request.from_consumer_and_token(
			self.consumer, 
			token, 
			http_method='DELETE', 
			http_url=url, 
		)
		return self._send_request(request, token)

	def put(self, path, post_params, token=None):
		url = "http://%s%s" % (self.host, path)
		request = oauth.Request.from_consumer_and_token(
			self.consumer,
			token,
			http_method='PUT',
			http_url=url,
			parameters=post_params
		)
		return self._send_request(request, token)

	def request_token(self):
		response = self.get(self.request_token_url).read()
		token = oauth.Token.from_string(response)
		return token 
	
	def authorize(self, token, callback_url = "oob"):
		http_url='http://%s%s' % (self.authority, self.authorize_url)
		request = oauth.Request.from_token_and_callback(token=token, callback=callback_url, http_url='http://%s%s' % (self.authority, self.authorize_url))
		return request.to_url()

	def access_token(self, request_token):
		response = self.get(self.access_token_url, request_token).read()
		return oauth.Token.from_string(response)

	def _send_request(self, request, token=None):
		request.sign_request(oauth.SignatureMethod_HMAC_SHA1(), self.consumer, token)
		conn = self._get_conn()
		if request.method == 'POST':
			body=request.to_postdata()
			conn.request('POST', request.url, body=request.to_postdata(), headers={"Content-type": "application/x-www-form-urlencoded"})
		elif request.method == 'DELETE':
			conn.request('DELETE', request.url, headers=request.to_header())
		else:
			conn.request('GET', request.url, headers=request.to_header())
		return conn.getresponse()

	def _get_conn(self):
		return httplib.HTTPConnection("%s:%d" % (self.host, self.port))

class MendeleyRemoteMethod(object):
	"""Call a Mendeley OpenAPI method and parse and handle the response"""
	def __init__(self, details, callback):
		self.details = details # Argument, URL and additional details.
		self.callback = callback # Callback to actually do the remote call
	
	def __call__(self, *args, **kwargs):
		url = self.details['url']
		# Get the required arguments 
		if self.details.get('required'):
			required_args = dict(zip(self.details.get('required'), args))
			if len(required_args) < len(self.details.get('required')):
				raise ValueError('Missing required args')

			for (key, value) in required_args.items():
				required_args[key] = urllib.quote_plus(str(value))

			url = url % required_args

		# Optional arguments must be provided as keyword args
		optional_args = {}
		for optional in self.details.get('optional', []):
			if kwargs.has_key(optional):
				optional_args[optional] = kwargs[optional]

		# Do the callback - will return a HTTPResponse object
		response = self.callback(url, self.details.get('access_token_required', False), self.details.get('method', 'get'), optional_args)
		status = response.status
		body = response.read()
		print body
		if status == 500:
			raise Exception(body)
		if status != 204:
			data = json.loads(body)
			return data

class MendeleyClient(object):
	# API method definitions. Used to create MendeleyRemoteMethod instances
	methods = {
		'details': {
			'required': ['id'],
			'optional': ['type'],
			'url': '/oapi/documents/details/%(id)s/',
		},
		'categories': {
			'url': '/oapi/documents/categories/',	
		},
		'subcategories': {
			'url': '/oapi/documents/subcategories/%(id)s/',
			'required': ['id'],
		},
		'search': {
			'url': '/oapi/documents/search/%(query)s/',
			'required': ['query'],
			'optional': ['page', 'items'],
		},
		'tagged': {
			'url': '/oapi/documents/tagged/%(tag)s/',
			'required': ['tag'],
			'optional': ['cat', 'subcat', 'page', 'items'],
		},
		'related': {
			'url': '/oapi/documents/related/%(id)s/', 
			'required': ['id'],
			'optional': ['page', 'items'],
		},
		'authored': {
			'url': '/oapi/documents/authored/%(author)s/',
			'required': ['author'],
			'optional': ['page', 'items'],
		},
		'author_stats': {
			'url': '/oapi/stats/authors/',
			'optional': ['discipline', 'upandcoming'],
		},
		'paper_stats': {
			'url': '/oapi/stats/authors/',
			'optional': ['discipline', 'upandcoming'],
		},
		'publication_stats': {
			'url': '/oapi/stats/authors/',
			'optional': ['discipline', 'upandcoming'],
		},
		'tag_stats': {
			'url': '/oapi/stats/tags/%(discipline)s/',
			'required': ['discipline'],
			'optional': ['upandcoming'],
		},
		# User specific methods
		'library_author_stats': {
			'url': '/oapi/library/authors/',
			'access_token_required': True,
		},
		'library_tag_stats': {
			'url': '/oapi/library/tags/',
			'access_token_required': True,
		},
		'library_publication_stats': {
			'url': '/oapi/library/publications/',
			'access_token_required': True,
		},
		'library': {
			'url': '/oapi/library/',
			'optional': ['page', 'items'],
			'access_token_required': True,
		},
		'collections': {
			'url': '/oapi/library/collections/',
			'access_token_required': True,
		},
		'sharedcollections': {
			'url': '/oapi/library/sharedcollections/',
			'access_token_required': True,
		},
		'document_details': {
			'url': '/oapi/library/documents/%(id)s/',
			'required': ['id'],
			'access_token_required': True,
		},
		'documents_authored': {
			'url': '/oapi/library/documents/authored/',
			'access_token_required': True,
		},
		'collection_documents': {
			'url': '/oapi/library/collections/%(id)s/',
			'required': ['id'],
			'optional': ['page', 'items'],
			'access_token_required': True,
		},
		'sharedcollection_documents': {
			'url': '/oapi/library/sharedcollections/%(id)s/',
			'required': ['id'],
			'optional': ['page', 'items'],
			'access_token_required': True,
		},
		'sharedcollection_members': {
			'url': '/oapi/library/sharedcollections/%(id)s/members/', 
			'required': ['id'],
			'access_token_required': True,
		},
		# Write methods
		'delete_collection': {
			'url': '/oapi/library/collections/%(id)s/',
			'required': ['id'],
			'access_token_required': True,
			'method': 'delete',
		},
		'delete_sharedcollection': {
			'url': '/oapi/library/sharedcollections/%(id)s/',
			'required': ['id'],
			'access_token_required': True,
			'method': 'delete',
		},
		'create_collection': {
			'url': '/oapi/library/collections/',
			# HACK: 'collection' is required, but by making it optional here it'll get POSTed
			# Unfortunately that means it needs to be a named param when calling this method
			'optional': ['collection'],
			'access_token_required': True,
			'method': 'post',
		},
		'create_sharedcollection': {
			'url': '/oapi/library/sharedcollections/',
			'optional': ['sharedcollection'],
			'access_token_required': True,
			'method': 'post',
		},
		'add_document_to_collection': {
			'url': '/oapi/library/collections/add/%(collection_id)s/%(document_id)s/',
			'required': ['collection_id', 'document_id'],
			'access_token_required': True,
			'method': 'post',
		},
		'remove_document_from_collection': {
			'url': '/oapi/library/collections/%(collection_id)s/%(document_id)s/',
			'required': ['collection_id', 'document_id'],
			'access_token_required': True,
			'method': 'delete',
		},
		'delete_sharedcollection_document': {
			'url': '/oapi/library/sharedcollections/%(collection_id)s/%(document_id)s/',
			'required': ['collection_id', 'document_id'],
			'access_token_required': True,
			'method': 'delete',
		},
		'delete_library_document': {
			'url': '/oapi/library/documents/%(id)s/',
			'required': ['id'],
			'access_token_required': True,
			'method': 'delete',
		},
		'create_document': {
			'url': '/oapi/library/documents/',
			# HACK: 'document' is required, but by making it optional here it'll get POSTed
			# Unfortunately that means it needs to be a named param when calling this method
			'optional': ['document'],
			'access_token_required': True,
			'method': 'post',
		},
		'contacts': {
			'url': '/oapi/profiles/contacts/',
			'access_token_required': True,
		        'method': 'get',	
		}, 
		'contacts_of_contact': {
			'url': '/oapi/profiles/contacts/%(id)s/', 
			'required': ['id'],
			'access_token_required': True, 
			'method': 'get',
		},
		'add_contact': {
			'url': '/oapi/profiles/contacts/%(id)s/',
			'required': ['id'],
			'access_token_required': True,
			'method': 'post',
		}
	}

	def __init__(self, consumer_key, consumer_secret):
		self.mendeley = OAuthClient(consumer_key, consumer_secret)
		# Create methods for all of the API calls	
		for method, details in self.methods.items():
			setattr(self, method, MendeleyRemoteMethod(details, self.api_request))

	def api_request(self, url, access_token_required = False, method = 'get', params = {}):
		if access_token_required: access_token = self.access_token
		else: access_token = None
		
		if method == 'get':
			if len(params) > 0:
				url += "?%s" % urllib.urlencode(params)
			response = self.mendeley.get(url, access_token)
		elif method == 'delete':
			response = self.mendeley.delete(url, access_token)
		else:
			response = self.mendeley.post(url, params, access_token)
		return response

	def get_required_keys(self):
		self.request_token = self.mendeley.request_token()
		auth_url = self.mendeley.authorize(self.request_token)
		print 'Go to the following url to auth the token:\n%s' % (auth_url,)
		verifier = raw_input('Enter verification code: ')
		self.request_token.set_verifier(verifier)
		self.access_token = self.mendeley.access_token(self.request_token)
	
	def load_keys(self):
		data = pickle.load(open('mendeley_api_keys.pkl', 'r'))
		self.request_token = data['request_token']
		self.access_token = data['access_token']

	def save_keys(self):
		data = {'request_token': self.request_token, 'access_token': self.access_token}
		pickle.dump(data, open('mendeley_api_keys.pkl', 'w'))
