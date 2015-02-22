# -*- coding: utf-8 -*-

import json
from xml.etree import ElementTree
import utils
import axeda_api
from cloud import Cloud

class Mashery(axeda_api.Axeda):
	"""
	Wind River Mashery API
	http://windriver.mashery.com/io-docs
	"""
	def __init__(self, config):
		Cloud.__init__(self, "Axeda", config)

		if not config.get("name"):
			assert(False)

		if not config.get("api_key"):
			assert(False)

		if not config.get("asset"):
			assert(False)

		if not config.get("model"):
			assert(False)

		self.config = config

		self.api_key = config["api_key"]
		# Service Requires SSL
		self.ssl = config.get('ssl')
		self.debug = config["debug"] if config.get('debug') else False
		self.name_space = None

		# Always use v1
		host = 'https://windriver.api.mashery.com/'
		self.url_prefix = host + config['name'] +  '/services/v1/rest/'

	def setURL(self, api):
		return self.url_prefix + api + '?api_key=' + self.api_key

	def setHeaders(self, json = None):
		# Always return response with json
		headers = { 'Accept': 'application/json' }

		if json == True or (json == None and self.json):
			headers["Content-Type"] = "application/json"
		# By default, return xml response or plain text by certain scripto

		return headers

	def scripto(self):
		return Scripto(self.config)

	def asset(self):
		return Asset(self.config)

	def dataItem(self):
		return DataItem(self.config)

class Scripto(Mashery, axeda_api.Scripto):
	def __init__(self, config):
		Mashery.__init__(self, config)
		self.url_prefix = self.url_prefix + 'Scripto/'
		self.api_key = self.get('api_key')

	def execute(self, app, data = None):
		self.checkParameter((app,))

		url = self.setURL('execute/' + app)

		headers = self.setHeaders(json = False)

		r = self.postRequest(url, headers, data)
		if r.status_code == 200:
			return r.content
		else:
			return None

class Asset(Mashery, axeda_api.Asset):
	"""
	Asset Object APIs
	"""
	def __init__(self, config):
		Mashery.__init__(self, config)
		self.url_prefix = self.url_prefix + 'asset/'
		self.api_key = self.get('api_key')

class DataItem(Mashery, axeda_api.DataItem):
	"""
	DataItemBridge. See Axeda_v2_API_Services_Developers_Reference_Guide_6.8
	"""
	def __init__(self, config):
		Mashery.__init__(self, config)
		self.url_prefix = self.url_prefix + 'dataItem/'
		self.api_key = self.get('api_key')
