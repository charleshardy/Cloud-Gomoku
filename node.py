# -*- coding: utf-8 -*-

from mashery_api import *
from axeda_api import *

class Node():
	"""
	A node indicates a machine or whatever connected to cloud.
	Its role may be client, server or whatever.
	"""
	def __init__(self, name, config):
		if not name:
			assert(False)

		if not config:
			assert(False)

		self.config = config
		if name == "Mashery":
			self.cloud = Mashery(config)
		elif name == "Axeda":
			self.cloud = Axeda(config)
			pass
		else:
			print("cloud is not configured")
			assert(False)

	def dataId(self, name):
		"""
		@id: data item name

		Return: string or None
		"""
		return name

	def setData(self, id, value):
		"""
		@id: data item name
		@value: string data to be stored

		Return: boolean
		"""
		scripto = self.cloud.scripto()
		r = scripto.execute('vlvFastSetPlatformData', data = {
			"dataItemName": id,
			"dataItemValue": str(value)
		})

		if r:
			return json.loads(r).get("msg") == "success"
		else:
			return False

	def getData(self, id):
		"""
		@id: data item name

		Return: string or None
		"""
		scripto = self.cloud.scripto()
		r = scripto.execute('vlvFastGetPlatformData', data = {
			"dataItemName": id,
		})

		if r:
			r = json.loads(r)
			if r.get("msg") == "success":
				return r.get("val")

		return None

	def getHistoricalData(self, name, **p):
		"""
		@name: data item name
		@p:
		- assetId: system id assigned to the asset
		- dataItemIds: list of system id assigned to the data items
		
		Return: string list or None
		"""
		asset_id = p.get("assetId")
		if not asset_id:
			if not p.get("modelNumber"):
				model = self.cloud["model"]
			else:
				model = p["modelNumber"]

			if not p.get("serialNumber"):
				serial = self.cloud["asset"]
			else:
				serial = p["serialNumber"]

			s = TypeAssetCriteria(**{
				"modelNumber": model,
				"serialNumber": serial
			})
			asset = self.cloud.asset()
			r = asset.findOne(s)
			if not r:
				print("Not found the asset %s (model: %s)" % (self.cloud["asset"], self.cloud["model"]))
				return None

			asset_id = r['systemId']

		s = TypeAbstractSearchCriteria(p.get("pageSize"), p.get("pageNumber"), p.get("sortAscending"), p.get("sortPropertyName")).getValue()
		c = TypeHistoricalDataItemValueCriteria(asset_id, p.get("dataItemIds"), p.get("startDate"), p.get("endDate")).getValue()
		s.update(c)

		dataitem = self.cloud.dataItem()
		r = dataitem.findHistoricalValues(**s)
		if not r:
			return None

		values = []
		# Find if the server variables were created.
		for dataItemValue in r["dataItemValues"]:
			dataItem = dataItemValue["dataItem"]
			#print("[%s] Data \"%s\" = %s, type %s" % (dataItem["systemId"], dataItem["name"], dataItemValue["value"], dataItem["type"]))
			if name != dataItem["name"]:
				continue
			#print("Data id %d, value %s" % (int(dataItem["systemId"]), dataItemValue["value"]))
			values.append(dataItemValue["value"])

		if self.cloud.isDebug():
			print values

		return values