# -*- coding: utf-8 -*-

import json
from xml.etree import ElementTree
import utils

# http://windriver.mashery.com/io-docs

class Criteria(dict):
	"""
	Format:
	@name: string
	@alias: string
	@modelId: int
	Model system id.
	@types: list
	@readOnly: bool
	@visible: bool
	@forwarded: bool
	@historicalOnly: null
	@pageSize: null
	@pageNumber: int
	Using the pageNumber pagination property affects which found object
	is returned by the findOne method. For example, pageNumber=1 returns the
	first matching found object, while pageNumber=3 returns the 3rd matching
	found object, etc.
	@sortAscending: bool
	@sortPropertyName: string
	e.g, "name"
	"""
	def __init__(self, criteria):
		dict.__init__(self, criteria)

class CurrentDataItemValueCriteria(dict):
	"""
	Format:
	@name: string
	@alias: string
	@assetId: int
	Asset system id.
	@types: list
	@readOnly: bool
	@visible: bool
	@forwarded: bool
	@historicalOnly: null
	@pageSize: null
	@pageNumber: int
	Using the pageNumber pagination property affects which found object
	is returned by the findOne method. For example, pageNumber=1 returns the
	first matching found object, while pageNumber=3 returns the 3rd matching
	found object, etc.
	@sortAscending: bool
	@sortPropertyName: string
	e.g, "name"
	"""
	def __init__(self, criteria):
		dict.__init__(self, criteria)

class Mashery(dict):
	'''
	Available server names:
	- ems (windriver.axeda.com)

	API doc:
	http://windriver.mashery.com/io-docs
	'''
	def __init__(self, config):
		dict.__init__(self, config)

		if self.get("cloud") != "Mashery":
			assert(False)

		if not self.get("name"):
			assert(False)

		if not self.get("api_key"):
			assert(False)

		if not self.get("asset"):
			assert(False)

		if not self.get("model"):
			assert(False)

		self.config = config

		self.api_key = config["api_key"]
		# Service Requires SSL
		self.ssl = self.get('ssl')
		self.name_space = None

		# Always use v1
		host = 'https://windriver.api.mashery.com/'
		self.url_prefix = host + config['name'] +  '/services/v1/rest/'

	def check_parameter(self, opts):
		for o in opts:
			if not o:
				assert(False)

	def __construct_request(self, api, json):
		url = self.url_prefix + api + '?api_key=' + self.api_key

		# Always return json response
		headers = { 'Accept': 'application/json' }
		if json:
			headers['Content-Type'] = 'application/json'
		# By default, return xml response

		return url, headers

	def get_request(self, api):
		url, headers = self.__construct_request(api, json = False)
		return utils.get(url, headers, ssl = self.ssl)

	def post_request(self, api, body, json = False):
		url, headers = self.__construct_request(api, json)
		return utils.post(url, headers, body, ssl = self.ssl)

	def put_request(self, api, body, json = False):
		url, headers = self.__construct_request(api, json)
		return utils.put(url, headers, body, ssl = self.ssl)

	def delete_request(self, api):
		url, headers = self.__construct_request(api, json = False)
		return utils.delete(url, headers, ssl = self.ssl)

	def getRecentlyViewed(self, key):
		"""
		Get Recently Viewed Asset
		An Asset is generally any piece of equipment that a company owns that could
		benefit by being remotely monitored and managed. Remote monitoring and
		management can reduce downtime, decrease service calls, and improve customer
		satisfaction. An Asset can be any piece of equipment you would like to
		monitor with the Axeda Platform.
		"""
		url = self.url_prefix + 'asset/recentlyViewed?api_key=' + self.api_key
		utils.parse_xml(self.get(url, self.ssl).content, key, name_space = None)

	def dataId(self, name):
		return name

	def setData(self, id, value):
		# FIXME
		scripto = Scripto(self.config)
		r = scripto.execute('vlvFastSetPlatformData', data = {
			"dataItemName": id,
			"dataItemValue": str(value)
		})

		if r:
			return json.loads(r)
		else:
			return None

	def getData(self, name):
		asset = Asset(self.config)
		r = asset.findOne(self["asset"], self["model"])
		if not r:
			print("Not found the asset %s (model: %s)" % (self["asset"], self["model"]))
			return None

		asset_id = r['systemId']
		#print("asset id = %s" % asset_id)
		#print("model id = %s" % r["model"]["systemId"])

		dataitem = DataItem(self.config)
		r = dataitem.findCurrentValues({ "assetId": asset_id })

		# Find if the server variables were created.
		for dataItemValue in r["dataItemValues"]:
			dataItem = dataItemValue["dataItem"]
			#print("[%s] Data \"%s\" = %s, type %s" % (dataItem["systemId"], dataItem["name"], dataItemValue["value"], dataItem["type"]))
			if name != dataItem["name"]:
				continue
			#print("Data id %d, value %s" % (int(dataItem["systemId"]), dataItemValue["value"]))
			return dataItemValue["value"]

		print("Not found the data %s" % name)
		return None

class Asset(Mashery):
	"""
	Asset Object APIs
	"""
	def __init__(self, config):
		Mashery.__init__(self, config)
		self.url_prefix = self.url_prefix + 'asset/'
		self.api_key = self.get('api_key')

	def find(self, serial_number):
		self.check_parameter((serial_number,))

		if False:
			payload = json.dumps({
				"modelNumber": serial_number,
			})
		else:
			payload = \
			'''<AssetCriteria xmlns="http://www.axeda.com/services/v2">
<serialNumber>''' + serial_number + '''</serialNumber></AssetCriteria>'''

		r = self.post_request('findOne', payload)
		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def findOne(self, serial_number = "*", model_name = "*"):
		self.check_parameter((serial_number, model_name))

		if True:
			payload = json.dumps({
				"modelNumber": model_name,
				"serialNumber": serial_number
			})
		else:
			payload = \
			'''<AssetCriteria xmlns="http://www.axeda.com/services/v2">
<modelNumber>''' + model_name + '''</modelNumber>
<serialNumber>''' + serial_number + '''</serialNumber>
</AssetCriteria>'''

		r = self.post_request('findOne', payload, json = True)
		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def findByIds(self, asset_id, fast = True):
		"""
		Finds the specified SDK objects based on the ids provided, and returns an
		unordered list of found objects. This method will accept only platform ids,
		and does not support aternate ids.
		"""
		self.check_parameter((asset_id,))

		if fast:
			r = self.get_request("id/" + str(asset_id))
		else:
			if False:
				payload = json.dumps({
					"id": asset_id
				})
			else:
				payload = \
				'''<IdCollection xmlns="http://www.axeda.com/services/v2">
	<id>''' + str(asset_id) + '''</id></IdCollection>'''

			r = self.post_request('findByIds', payload)

		if r.status_code == 200:
			return r.content
		else:
			return None

class DataItem(Mashery):
	'''
	DataItemBridge. See Axeda_v2_API_Services_Developers_Reference_Guide_6.8
	'''
	def __init__(self, config):
		Mashery.__init__(self, config)
		self.url_prefix = self.url_prefix + 'dataItem/'
		self.api_key = self.get('api_key')

	def create(self, name, model_name, type, alias = ""):
		"""
		Creates a new Data Item.

		@name:
		@model:
		@type:
			DIGITAL
			ANALOG
			STRING
		"""
		self.check_parameter((name, model_name, type))

		if type not in ("DIGITAL", "ANALOG", "STRING"):
			assert(False)

		if False:
			payload = json.dumps({
				"name": "valvrave_test_string",
				"type": "STRING",
			})
		else:
			payload = \
			'''<v2:DataItem xmlns:v2="http://www.axeda.com/services/v2">
<v2:name>''' + name + '''</v2:name>
<ns85:model id="''' + model_name + '''" xsi:type="ns85:ModelReference" xmlns:ns85="http://www.axeda.com/services/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
<v2:type>''' + type + '''</v2:type>
</v2:DataItem>'''

		r = self.put_request('', payload, json = False)
		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def save(self, name, model_name, type, alias = ""):
		"""
		Save a new Data Item.

		Note:
		This same REST call as a create() invokes a Save operation.

		@name:
		@model:
		@type:
			DIGITAL
			ANALOG
			STRING

		Return value:
		{
			"successful":true,
			"totalCount":1,
			"succeeded":[
			{
				"ref":"es2015-Galileo-Gen2||valvrave_test_string3",
				"id":"427"
			}],
			"failures":[]
		}
		"""
		self.check_parameter((name, model_name, type,))

		if type not in ("DIGITAL", "ANALOG", "STRING"):
			assert(False)

		if False:
			payload = json.dumps({
				"name": "valvrave_test_string",
				"id": "es2015-Galileo-Gen2||valvrave_test_string",
				"type": "STRING",
			})
		else:
			payload = \
			'''<v2:DataItem xmlns:v2="http://www.axeda.com/services/v2">
<v2:name>''' + name + '''</v2:name>
<ns85:model id="''' + model_name + '''" xsi:type="ns85:ModelReference" xmlns:ns85="http://www.axeda.com/services/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
<v2:type>''' + type + '''</v2:type>
</v2:DataItem>'''

		r = self.post_request('', payload, json = False)
		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def update(self, dataitem_id, name, model_name, type, alias = ""):
		"""
		Updates an existing Data Item.
		"""
		self.check_parameter((dataitem_id, name, model_name, type))

		if type not in ("DIGITAL", "ANALOG", "STRING"):
			assert(False)

		if False:
			payload = json.dumps(
			{
				"name": name,
				"model": [{
					"objType": "ModelReference", "id": model
				}],
				"type": type
			})
		else:
			payload = \
			'''<v2:DataItem xmlns:v2="http://www.axeda.com/services/v2" systemId="''' + str(dataitem_id) + '''">
<v2:name>''' + name + '''</v2:name>
<ns85:model id="''' + model_name + '''" xsi:type="ns85:ModelReference" xmlns:ns85="http://www.axeda.com/services/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
<v2:type>''' + type + '''</v2:type>
<v2:alias>''' + alias + '''</v2:alias>
</v2:DataItem>'''

		r = self.post_request('id/' + str(dataitem_id), payload, json = False)
		if r.status_code == 200:
			return r.content
		else:
			return None

	def delete(self, dataitem_id):
		"""
		Deletes a data item.
		"""
		self.check_parameter((dataitem_id,))

		r = self.delete_request('id/' + str(dataitem_id))
		if r.status_code == 200:
			return r.content
		else:
			return None

	def find(self, criteria):
		"""
		Finds Data Items based on search criteria.

		@criteria: See the class Criteria.
		"""
		self.check_parameter((criteria,))
		c = Criteria(criteria)

		if True:
			payload = json.dumps(c)
		else:
			payload = None

		r = self.post_request('find', payload, json = True)
		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def findOne(self, criteria):
		"""
		Returns the first Data Item found that meets specified search criteria.

		@criteria: See the class Criteria.

		Note:
		Essentially this API equals to find() with pageNumber=1.
		"""
		self.check_parameter((criteria,))
		c = Criteria(criteria)

		if True:
			payload = json.dumps(c)
		else:
			payload = None

		r = self.post_request('findOne', payload, json = True)
		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def findByIds(self, dataitem_ids):
		"""
		Finds the specified SDK objects based on the ids provided, and returns an
		unordered list of found objects. This method will accept only platform ids,
		and does not support aternate ids.
		"""
		self.check_parameter((dataitem_ids,))

		if False:
			payload = json.dumps({
				"id": dataitem_id
			})
		else:
			payload = '''<IdCollection xmlns="http://www.axeda.com/services/v2">'''
			for i in dataitem_ids:
				payload += '<id>' + str(i) + '</id>'
			payload += '</IdCollection>'

		r = self.post_request('findByIds', payload)

		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def findById(self, dataitem_id):
		"""
		Finds an Data Item based on its platform identifier.

		@dataitem_id
		"""
		self.check_parameter((dataitem_id,))

		r = self.get_request('id/' + str(dataitem_id))

		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def findByAlternateId(self, name, model_name):
		"""
		Finds a Data Item based on the alternate identifier.

		@alternate_id
		The alternate ID of a Data Item takes the following format:
		ModelNumber||dataItemName
		"""
		self.check_parameter((name, model_name))

		alternate_id = model_name + "||" + name
		r = self.get_request(alternate_id)

		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def findCurrentValues(self, criteria):
		"""
		Returns the current values of the specified Data Items.

		Note:
		For the findCurrentValues method, the assetId input field is required.
		"""
		self.check_parameter((criteria,))

		c = CurrentDataItemValueCriteria(criteria)

		if True:
			payload = json.dumps(c)
		else:
			payload = \
			'''<v2:CurrentDataItemValueCriteria sortAscending="true" sortPropertyName="name" xmlns:v2="http://www.axeda.com/services/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<v2:assetId>''' + str(criteria['asset_id']) + '''</v2:assetId></v2:CurrentDataItemValueCriteria>'''

		r = self.post_request('findCurrentValues', payload, json = True)
		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def findHistoricalValues(self):
		"""
		Returns the historical values of the specified Data Items.
		"""
		pass

	def getSourceDataItems(self, id):
		"""
		Returns the source Data Items associated with the specified source Data Item.
		"""
		self.check_parameter((id,))

		r = self.get_request('id/' + str(id) + '/sourceDataItems')

		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def getTargetDataItems(self, id):
		"""
		Returns the source Data Items associated with the specified target Data Item.
		"""
		self.check_parameter((id,))

		r = self.get_request('id/' + str(id) + '/targetDataItems')

		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def bulkCreate(self):
		pass

	def bulkDelete(self):
		pass

	def bulkSave(self):
		pass

	def bulkUpdate(self):
		pass

class Scripto(Mashery):
	'''
	https://windriver.axeda.com/services/v1/rest/Scripto/?_wadl
	'''
	def __init__(self, config):
		Mashery.__init__(self, config)
		self.url_prefix = self.url_prefix + 'Scripto/'
		self.api_key = self.get('api_key')

	def execute(self, app, data = None):
		self.check_parameter((app,))

		r = self.post_request('execute/' + app, data)
		if r.status_code == 200:
			return r.content
		else:
			return None
