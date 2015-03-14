# -*- coding: utf-8 -*-

import utils

class Cloud(dict):
	def __init__(self, name, config):
		if not name:
			assert(False)

		if not config:
			assert(False)

		dict.__init__(self, config)
		self.name = name

	def name(self):
		return self.name

	def checkParameter(self, opts):
		for o in opts:
			if not o:
				assert(False)

	def getRequest(self, url, headers, data = None):
		return utils.get(url, headers, data, ssl = self.ssl)

	def postRequest(self, url, headers, data):
		return utils.post(url, headers, data, ssl = self.ssl)

	def putRequest(self, url, headers, data):
		return utils.put(url, headers, data, ssl = self.ssl)

	def deleteRequest(self, url, headers):
		return utils.delete(url, headers, ssl = self.ssl)
