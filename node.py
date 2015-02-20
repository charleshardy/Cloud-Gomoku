# -*- coding: utf-8 -*-

import mashery_api

class Node():
	"""
	A node indicates a machine or whatever connected to cloud.
	Its role may be client, server or whatever.
	"""
	def __init__(self, config = None):
		if not config:
			assert(False)

		if config.get("cloud") == "Mashery":
			self.cloud = mashery_api.Mashery(config)
		elif config.get("cloud") == "Axeda":
			self.cloud = axeda_api.Axeda(config)
		else:
			print("cloud is not configured")
			assert(False)

	def dataId(self, name):
		return self.cloud.dataId(name)

	def setData(self, name, value):
		return self.cloud.setData(name, value)

	def getData(self, name):
		return self.cloud.getData(name)
