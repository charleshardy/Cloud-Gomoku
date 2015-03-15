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

		self.name_mapping = {}

	def dataId(self, name):
		"""
		@id: data item name

		Return: string or None
		"""
		return name

	def dataSystemId(self, name):
		if name in self.name_mapping:
			return self.name_mapping[name]

		dataItem = self.cloud.dataItem()
		s = TypeDataItemCriteria(**{
			"name": name,
			"types": ["STRING"],
		}).getValue()
		r = dataItem.findOne(**s)
		if not r:
			print("dataId: not found the data item %s" % name)
			return None

		id = r["systemId"]
		self.name_mapping[name] = id
		return id

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
			if self.cloud.isDebug():
				print("setData: %s" % r)
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
			if self.cloud.isDebug():
				print("getData: %s" % r)

			r = json.loads(r)
			if r.get("msg") == "success":
				return r.get("val")

		return None

	def deleteData(self, name):
		"""
		@name: data item name

		Return: string or None
		"""
		dataItem = self.cloud.dataItem()
		s = TypeDataItemCriteria(**{
			"name": name,
			"types": ["STRING"],
		}).getValue()
		r = dataItem.findOne(**s)
		if not r:
			print("deleteData: not found the data item %s" % name)
			return None

		r = dataItem.delete(r["systemId"])
		if not r:
			print("deleteData: fail to delete data item %s" % name)
			return None

		return r

	def deleteDatas(self, name_pattern):
		dataItem = self.cloud.dataItem()
		s = TypeDataItemCriteria(**{
			"name": name_pattern,
			"types": ["STRING"],
		}).getValue()
		r = dataItem.find(**s)
		if not r:
			print("deleteDatas: not found the data item %s" % name_pattern)

		for d in r["dataItems"]:
			j = dataItem.delete(d["systemId"])
			if not j:
				print("deleteDatas: fail to delete data items %s" % name_pattern)
				return None
			print("deleteDatas: %s deleted" % d["name"])

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

		if not p.get("dataItemIds"):
			# Search dataitem id
			dataItem = self.cloud.dataItem()
			s = TypeDataItemCriteria(**{
				"name": name,
				#"modelId": p.get("modelId"),
				"types": ["STRING"],
				#"readOnly": p.get("readOnly"),
				#"visible": p.get("visible"),
				#"historicalOnly": p.get("historicalOnly"),
			}).getValue()
			r = dataItem.findOne(**s)
			if not r:
				print("Not found the data item id for %s (asset: %s, model: %s)" % (name, self.cloud["asset"], self.cloud["model"]))
				return None

			dataItemIds = [r["systemId"]]
		else:
			dataItemIds = p["dataItemIds"]

		if self.cloud.isDebug():
			print "asset id: ", asset_id

		s = TypeAbstractSearchCriteria(p.get("pageSize"), p.get("pageNumber"), p.get("sortAscending"), p.get("sortPropertyName")).getValue()
		c = TypeHistoricalDataItemValueCriteria(asset_id, dataItemIds, p.get("startDate"), p.get("endDate")).getValue()
		s.update(c)

		dataitem = self.cloud.dataItem()
		r = dataitem.findHistoricalValues(**s)
		if not r:
			return None

		values = []
		# Find if the server variables were created.
		for dataItemValue in r["dataItemValues"]:
			dataItem = dataItemValue["dataItem"]
			if self.cloud.isDebug():
				print("[%s] Data \"%s\" = %s, timestamp %s" % (dataItem["systemId"], dataItem["name"], dataItemValue["value"], dataItemValue["timestamp"]))
			values.append(dataItemValue["value"])

		return values