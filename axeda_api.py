# -*- coding: utf-8 -*-

import json
from xml.etree import ElementTree
import utils
from cloud import Cloud

def toString(c):
	return str(c) if c != None else None

def toBool(c):
	return bool(c) if c != None else None

def toInt(c):
	return int(c) if c != None else None

def toList(c):
	return list(c) if c != None else None

def toDateTime(c):
	"""
	FIXME
	"""
	return None

class TypeabstractPlatformObjectBase(object):
	def __init__(self, val, **p):
		val.update(p)
		self.stored_value = val

	def getValue(self):
		if not self.stored_value:
			return None

		return self.stored_value

	def toJson(self):
		return json.dumps(self.stored_value)

	def toXml(self):
		pass

class TypeAbstractPlatformObject(TypeabstractPlatformObjectBase):
	"""
	Format: attributes
	@id: string
	@systemId: string
	@label: string
	@detail: string
	@restUrl: string
	"""
	def __init__(self, id, systemId, label, detail, restUrl):
		TypeabstractPlatformObjectBase.__init__(self, {
			"id": id,
			"systemId": systemId,
			"label": label,
			"detail": detail,
			"restUrl": restUrl
		})

class TypeDataItemReference(TypeAbstractPlatformObject):
	def __init__(self, id, systemId, label, detail, restUrl):
		TypeAbstractPlatformObject.__init__(self, id, systemId, label, detail, restUrl)

class TypeDataItemCollection(TypeabstractPlatformObjectBase):
	"""
	Format:
	@dataItem: list of DataItemReference
	"""
	def __init__(self, dataItemRefernences):
		for i in dataItemRefernences:
			TypeAbstractPlatformObject(i)
		dict.__init__(self, list(dataItemRefernences))

class TypeAbstractSearchCriteria(TypeabstractPlatformObjectBase):
	"""
	Format:
	attributes
	@pageSize: int
	Specify the number of entries per page of the results, if not specified defaults to MAX_PAGE_SIZE
	@pageNumber: int
	Specify which page of the results to return, if not specified defaults to DEFAULT_PAGE.
	Using the pageNumber pagination property affects which found object
	is returned by the findOne method. For example, pageNumber=1 returns the
	first matching found object, while pageNumber=3 returns the 3rd matching
	found object, etc.
	@sortAscending: boolean
	@sortPropertyName: string
	"""
	def __init__(self, pageSize, pageNumber, sortAscending, sortPropertyName, **p):
		self.pageSize = toInt(pageSize)
		self.pageNumber = toInt(pageNumber)
		self.sortAscending = toBool(sortAscending)
		self.sortPropertyName = toString(sortPropertyName)

		TypeabstractPlatformObjectBase.__init__(self, {
			"pageSize": self.pageSize,
			"pageNumber": self.pageNumber,
			"sortAscending": self.sortAscending,
			"sortPropertyName": self.sortPropertyName
		}, **p)

class TypeDataItemCriteria(TypeAbstractSearchCriteria):
	"""
	Format:
	@name: string
	@alias: string
	@modelId: string
	Model system id.
	@types: list of DataItemType ("ANALOG" / "DIGITAL" / "STRING")
	@readOnly: boolean
	@visible: boolean
	@forwarded: boolean
	@historicalOnly: boolean
	e.g, "name"
	"""
	def __init__(self, **p):
		self.name = toString(p.get("name"))
		self.alias = toString(p.get("alias"))
		self.modelId = toString(p.get("modelId"))
		self.types = toList(p.get("types"))
		self.readOnly = toBool(p.get("readOnly"))
		self.visible = toBool(p.get("visible"))
		self.forwarded = toBool(p.get("forwarded"))
		self.historicalOnly = toBool(p.get("historicalOnly"))

		TypeAbstractSearchCriteria.__init__(self,
			pageSize = p.get("pageSize"),
			pageNumber = p.get("pageNumber"),
			sortAscending = p.get("sortAscending"),
			sortPropertyName = p.get("sortPropertyName"),
			**{
				"name": self.name,
				"alias": self.alias,
				"modelId": self.modelId,
				"types": self.types,
				"readOnly": self.readOnly,
				"visible": self.visible,
				"forwarded": self.forwarded,
				"historicalOnly": self.historicalOnly
			}
		)

class TypeHistoricalDataItemValueCriteria(TypeAbstractSearchCriteria):
	"""
	Format:
	@assetId: string
	@dataItemIds: list
	@  item: string
	@startDate: dateTime
	@endDate: dateTime
	"""
	def __init__(self, assetId, dataItemIds, startDate, endDate):
		self.assetId = toString(assetId)
		self.startDate = toDateTime(startDate)
		self.endDate = toDateTime(endDate)

		dataItemIds = toList(dataItemIds)
		d = []
		self.dataItemIds = []
		if dataItemIds:
			for i in dataItemIds:
				#d.append({"item": str(i)})
				d.append(str(i))
				self.dataItemIds.append(str(i))

		TypeabstractPlatformObjectBase.__init__(self, {
			"assetId": self.assetId,
			"dataItemIds": d,
			"startDate": self.startDate,
			"endDate": self.endDate
		})

class TypeSuccessfulOperation(TypeabstractPlatformObjectBase):
	def __init__(self, p):
		# FIXME: <xs:sequence>
		self.succeeded = []
		for s in toList(p):
			self.succeeded.append({
				"ref": toString(s.get("ref")),
				"id": toString(s.get("id"))
			})

		TypeabstractPlatformObjectBase.__init__(self, self.succeeded)

class TypeFailedOperationDetails(TypeabstractPlatformObjectBase):
	def __init__(self, p):
		# <xs:sequence/>
		TypeabstractPlatformObjectBase.__init__(self, toList(p))

class TypeFailedOperation(TypeabstractPlatformObjectBase):
	def __init__(self, p):
		# FIXME: <xs:sequence>
		self.failures = []
		for s in toList(p):
			self.failures.append({
				"ref": toString(s.get("ref")),
				"message": toString(s.get("message")),
				"details": TypeFailedOperationDetails(s.get("details")).getValue(),
				"sourceOfFailure": toString(s.get("sourceOfFailure")),
				# Attribute
				"code": toString(s.get("code"))
			})

		TypeabstractPlatformObjectBase.__init__(self, self.failures)

class TypeAbstractExecutionResult(TypeabstractPlatformObjectBase):
	def __init__(self, p):
		self.succeeded = TypeSuccessfulOperation(p.get("succeeded")).getValue()
		self.failures = TypeFailedOperation(p.get("failures")).getValue()
		# Attributes
		self.successful = toBool(p.get("successful"))
		self.totalCount = toInt(p.get("totalCount"))

		TypeabstractPlatformObjectBase.__init__(self, {
			"succeeded": self.succeeded,
			"failures": self.failures,
			"successful": self.successful,
			"totalCount": self.totalCount
		})

class TypeExecutionResult(TypeAbstractExecutionResult):
	def __init__(self, p):
		TypeAbstractExecutionResult.__init__(self, p)

class TypeAssetCriteria(TypeAbstractSearchCriteria):
	def __init__(self, **p):
		self.gatewayId = toString(p.get("gatewayId"))
		self.name = toString(p.get("name"))
		self.modelNumber = toString(p.get("modelNumber"))
		self.serialNumber = toString(p.get("serialNumber"))
		self.organizationName = toString(p.get("organizationName"))
		self.locationName = toString(p.get("locationName"))
		self.regionName = toString(p.get("regionName"))
		self.assetGroupName = toString(p.get("assetGroupName"))
		self.systemName = toString(p.get("systemName"))
		self.gatewayName = toString(p.get("gatewayName"))
		self.gatewayOnly = toBool(p.get("gatewayOnly"))
		self.backupAgentsOnly = toString(p.get("backupAgentsOnly"))
		self.packageName = toString(p.get("packageName"))
		self.packageVersion = toString(p.get("packageVersion"))
		self.withoutPackage = toBool(p.get("withoutPackage"))
		self.muted = toBool(p.get("muted"))
		self.conditionId = toString(p.get("conditionId"))
		self.toLastContactDate = toDateTime(p.get("toLastContactDate"))
		self.fromLastContactDate = toDateTime(p.get("fromLastContactDate"))
		#@dataItem: DataItemValueCriteria
		self.hasEventsSince = toDateTime(p.get("hasEventsSince"))
		#@geofence: GeofenceCriteria
		self.showAssetsWithAlarms = toBool(p.get("showAssetsWithAlarms"))
		self.propertyName = toString(p.get("propertyName"))
		#@item: string list
		#@propertyNamesMatchType：PropertyNamesMatchType
		self.propertyValue = toString(p.get("propertyValue"))
		self.includeDetails = toBool(p.get("includeDetails"))
		self.missing = toBool(p.get("missing"))
		self.neverRegistered = toBool(p.get("neverRegistered"))
		self.inMachineStream = toBool(p.get("inMachineStream"))

		TypeAbstractSearchCriteria.__init__(self,
			p.get("assetId"), p.get("dataItemIds"), p.get("startDate"), p.get("endDate")
		)

		TypeabstractPlatformObjectBase.__init__(self, {
			"gatewayId": self.gatewayId,
			"name": self.name,
			"modelNumber": self.modelNumber,
			"serialNumber": self.serialNumber,
			"organizationName": self.organizationName,
			"locationName": self.locationName,
			"regionName": self.regionName,
			"assetGroupName": self.assetGroupName,
			"systemName": self.systemName,
			"gatewayName": self.gatewayName,
			"gatewayOnly": self.gatewayOnly,
			"backupAgentsOnly": self.backupAgentsOnly,
			"packageName": self.packageName,
			"packageVersion": self.packageVersion,
			"withoutPackage": self.withoutPackage,
			"muted": self.muted,
			"conditionId": self.conditionId,
			"toLastContactDate": self.toLastContactDate,
			"fromLastContactDate": self.fromLastContactDate,
			#@dataItem: DataItemValueCriteria
			"hasEventsSince": self.hasEventsSince,
			#@geofence: GeofenceCriteria
			"showAssetsWithAlarms": self.showAssetsWithAlarms,
			"propertyName": self.propertyName,
			#@propertyNamesMatchType：PropertyNamesMatchType
			"propertyValue": self.propertyValue,
			"includeDetails": self.includeDetails,
			"missing": self.missing,
			"neverRegistered": self.neverRegistered,
			"inMachineStream": self.inMachineStream
		})

class CurrentDataItemValueCriteria(dict):
	"""
	Format:
	@name: string
	@alias: string
	@assetId: string
	Asset system id.
	@types: list
	@readOnly: boolean
	@visible: boolean
	@forwarded: boolean
	@historicalOnly: boolean
	@pageSize: int
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

class Axeda(Cloud):
	"""
	Axeda platform REST APIs
	https://<host>/artisan/apidocs/v1/
	https://<host>/artisan/apidocs/v2/
	"""
	def __init__(self, config):
		Cloud.__init__(self, "Axeda", config)

		if self.get('name') == None:
			assert(False)

		if self.get('username') == None:
			assert(False)

		if self.get('password') == None:
			assert(False)

		if not self.get("asset"):
			assert(False)

		if not self.get("model"):
			assert(False)

		self.config = config

		self.username = self.get('username')
		self.password = self.get('password')
		self.timeout = self.get('timeout')
		self.session_id = None

		if self.get('ssl') != None:
			self.ssl = self.get('ssl')
		else:
			self.ssl = None

		self.debug = config["debug"] if config.get('debug') else False

		# Use json or xml?
		if self.get('json') == None:
			self.json = True
		else:
			self.json = self.get('json')

		if self.ssl == True:
			self.v1_url_prefix = 'https'
			self.v2_url_prefix = 'https'
		else:
			self.v1_url_prefix = 'http'
			self.v2_url_prefix = 'http'
		self.v1_url_prefix += '://' + config['name'] + '/services/v1/rest/'
		self.v2_url_prefix += '://' + config['name'] + '/services/v2/rest/'

		if not self.json:
			self.name_space = 'http://type.v1.webservices.sl.axeda.com'
			ElementTree.register_namespace('', self.name_space)
			#ElementTree.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
		else:
			self.name_space = None

	def isDebug(self):
		return self.debug

	def checkParameter(self, opts):
		for o in opts:
			if not o:
				assert(False)

	def setURL(self, api):
		url = self.url_prefix + api

		if False:
			if self.session_id:
				url += '?sessionid=' + self.session_id
			else:
				url += '?username=' + self.username + '&password=' + self.password

		return url

	def setHeaders(self, json = None):
		# Always return json response
		headers = { "Accept": "application/json" }
		if json == True or (json == None and self.json == True):
			headers["Content-Type"] = "application/json"
		else:
			headers["Content-Type"] = "application/xml"
		# By default, return xml response or plain text by certain scripto

		if self.session_id:
			headers["x_axeda_wss_sessionid"] = self.session_id
		else:
			headers["x_axeda_wss_username"] = self.username
			headers["x_axeda_wss_password"] = self.password

		return headers

	def auth(self):
		return Auth(self.config)

	def scripto(self):
		return Scripto(self.config)

	def asset(self):
		return Asset(self.config)

	def dataItem(self):
		return DataItem(self.config)

class Auth(Axeda):
	"""
	API
	https://<host>/services/v1/rest/Auth?_wadl
	"""
	def __init__(self, config):
		Axeda.__init__(self, config, False)
		self.url_prefix = self.v1_url_prefix + 'Auth/'

	def login(self, username = None, password = None, timeout = 1800):
		"""
		Creates a new session (sessionId) for the related authenticated user.

		Note that when Axeda Platform creates a session for a user, a timeout is
		defined for that session. The session will be valid only while the session
		is effective; if the session times out, additional calls to the Web services
		will return “access defined” errors. Your code should implement error
		handling to ensure the session is still valid.
		"""
		if not username:
			username = self.username

		if not password:
			password = self.password

		if not timeout:
			timeout = self.timeout

		url = self.url_prefix + 'login?principal.username=' + username + \
			'&password=' + password + '&sessionTimeout=' + str(timeout)

		if self.json:
			headers = { 'Accept': 'application/json' }
		else:
			headers = None

		r = utils.get(url, headers = headers, ssl = self.ssl)
		if r.status_code != 200:
			return False

		if self.json:
			self.session_id = str(json.loads(r.content)['wsSessionInfo']['sessionId'])
		else:
			self.session_id = str(utils.parse_xml(r.content, 'sessionId', self.name_space))

		if self.session_id:
			return True
		else:
			return False

	def logout(self, sessionid = None):
		"""
		Ends the session for the related user. Invalidates the specified SessionId
		such that it can no	longer be used.
		"""
		if not self.session_id and not sessionid:
			return False

		url = self.url_prefix + 'logout?sessionid='
		if sessionid:
			url += sessionid
		else:
			url += self.session_id

		r = utils.get(url, ssl = self.ssl)
		if r.status_code != 204:
			return False
		else:
			self.session_id = None
			return True

class Scripto(Axeda):
	"""
	API
	https://<host>/services/v1/rest/Scripto/?_wadl
	"""
	def __init__(self, config, sessionid = None):
		Axeda.__init__(self, config)
		self.url_prefix = self.v1_url_prefix + 'Scripto/'
		self.session_id = sessionid

	def execute(self, app, data = None):
		self.checkParameter((app,))

		url = self.setURL('execute/' + app)

		headers = self.setHeaders(json = False)

		r = self.getRequest(url, headers, data)
		if r.status_code == 200:
			return r.content
		else:
			return None

class Asset(Axeda):
	"""
	Asset Object APIs
	https://<host>/services/v2/rest/asset?_wadl
	"""
	def __init__(self, config, sessionid = None):
		Axeda.__init__(self, config)
		self.url_prefix = self.v2_url_prefix + 'asset/'
		self.session_id = sessionid

	def find(self, serial_number):
		self.checkParameter((serial_number,))

		url = self.setURL("find")

		headers = self.setHeaders(json = False)

		if False:
			payload = json.dumps({
				"modelNumber": serial_number,
			})
		else:
			payload = \
			'''<AssetCriteria xmlns="http://www.axeda.com/services/v2">
<serialNumber>''' + serial_number + '''</serialNumber></AssetCriteria>'''

		r = self.postRequest(url, headers, payload)
		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def findOne(self, s):
		"""
		Finds the first Asset that meets the specified criteria.
		"""
		self.checkParameter((s,))
		if not isinstance(s, TypeAssetCriteria):
			assert(False)

		url = self.setURL("findOne")

		headers = self.setHeaders(json = True)

		# FIXME: either mode doesn't working with Axeda but Mashery.
		if True:
			payload = s.toJson()
		else:
			if True:
				payload = \
				'''<?xml version="1.0" encoding="UTF-8"?><AssetCriteria xmlns="http://www.axeda.com/services/v2"><modelNumber>''' + c["modelNumber"] + '''</modelNumber><serialNumber>''' + c["serialNumber"] + '''</serialNumber></AssetCriteria>'''
			else:	# also work with Mashery
				payload = \
				'''<v2:AssetCriteria sortAscending="true" sortPropertyName="name" xmlns:v2="http://www.axeda.com/services/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><v2:modelNumber>''' + c["modelNumber"] + '''</v2:modelNumber><v2:serialNumber>''' + c["serialNumber"] + '''</v2:serialNumber></v2:AssetCriteria>'''

		r = self.postRequest(url, headers, payload)
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
		self.checkParameter((asset_id,))

		if fast:
			url = self.setURL("id/" + str(asset_id))
			headers = self.setHeaders(json = False)
			r = self.getRequest(url, headers)
		else:
			url = self.setURL('findByIds')
			headers = self.setHeaders(json = False)

			if False:
				payload = json.dumps({
					"id": asset_id
				})
			else:
				payload = \
				'''<IdCollection xmlns="http://www.axeda.com/services/v2">
	<id>''' + str(asset_id) + '''</id></IdCollection>'''

			r = self.postRequest('findByIds', headers, payload)

		if r.status_code == 200:
			return r.content
		else:
			return None

class DataItem(Axeda):
	"""
	API
	https://<host>/services/v2/rest/dataItem?_wadl
	"""
	def __init__(self, config, sessionid = None):
		Axeda.__init__(self, config)
		self.url_prefix = self.v2_url_prefix + 'dataItem/'
		self.session_id = sessionid

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
		self.checkParameter((name, model_name, type))

		if type not in ("DIGITAL", "ANALOG", "STRING"):
			assert(False)

		url = self.setURL("")

		headers = self.setHeaders(json = False)

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

		r = self.putRequest(url, headers, payload)
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
		self.checkParameter((name, model_name, type,))

		if type not in ("DIGITAL", "ANALOG", "STRING"):
			assert(False)

		url = self.setURL("")

		headers = self.setHeaders(json = False)

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

		r = self.postRequest(url, headers, payload)
		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def update(self, dataitem_id, name, model_name, type, alias = ""):
		"""
		Updates an existing Data Item.
		"""
		self.checkParameter((dataitem_id, name, model_name, type))

		if type not in ("DIGITAL", "ANALOG", "STRING"):
			assert(False)

		url = self.setURL("id/" + str(dataitem_id))

		headers = self.setHeaders(json = False)

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

		r = self.postRequest(url, headers, payload)
		if r.status_code == 200:
			return r.content
		else:
			return None

	def delete(self, dataitem_id):
		"""
		Deletes a data item.
		"""
		self.checkParameter((dataitem_id,))

		url = self.setURL("id/" + str(dataitem_id))

		headers = self.setHeaders(json = False)

		r = self.deleteRequest(url, headers)
		if r.status_code == 200:
			#return TypeExecutionResult(json.loads(r.content))
			return json.loads(r.content)
		else:
			return None

	def find(self, **s):
		"""
		Finds Data Items based on search criteria.

		@criteria: a complete criteria is defined as:
        alias: (null)
        modelId: (null)
        types: ([])
        readOnly": (null)
        visible": (null)
        forwarded: (null)
        historicalOnly: (null)
        pageSize": (null)
        pageNumber: (null)
        sortAscending: (null)
        sortPropertyName: (null)
		"""
		url = self.setURL("find")

		headers = self.setHeaders(json = True)

		if True:
			payload = json.dumps(s)
		else:
			payload = None

		r = self.postRequest(url, headers, payload)
		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def findOne(self, **s):
		"""
		Returns the first Data Item found that meets specified search criteria.

		@criteria: See the class Criteria.

		Note:
		Essentially this API equals to find() with pageNumber=1.
		"""
		url = self.setURL("findOne")

		headers = self.setHeaders(json = True)

		if True:
			payload = json.dumps(s)
		else:
			payload = None

		r = self.postRequest(url, headers, payload)
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
		self.checkParameter((dataitem_ids,))

		url = self.setURL("findByIds")

		headers = self.setHeaders(json = False)

		if False:
			payload = json.dumps({
				"id": dataitem_id
			})
			# FIXME: which one
			payload = json.dumps({
				"dataItem": [{
					"systemId": str(dataitem_id)
				}]
			})
		else:
			payload = '''<IdCollection xmlns="http://www.axeda.com/services/v2">'''
			for i in dataitem_ids:
				payload += '<id>' + str(i) + '</id>'
			payload += '</IdCollection>'

		r = self.postRequest(url, headers, payload)

		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def findById(self, dataitem_id):
		"""
		Finds an Data Item based on its platform identifier.

		@dataitem_id
		"""
		self.checkParameter((dataitem_id,))

		url = self.setURL("id/" + str(dataitem_id))

		headers = self.setHeaders(json = False)

		r = self.getRequest(url, headers)

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
		self.checkParameter((name, model_name))

		alternate_id = model_name + "||" + name
		url = self.setURL(alternate_id)

		headers = self.setHeaders(json = False)

		r = self.getRequest(url, headers)

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
		self.checkParameter((criteria,))

		c = CurrentDataItemValueCriteria(criteria)

		url = self.setURL("findCurrentValues")

		headers = self.setHeaders(json = True)

		if True:
			payload = json.dumps(c)
		else:
			payload = \
			'''<v2:CurrentDataItemValueCriteria sortAscending="true" sortPropertyName="name" xmlns:v2="http://www.axeda.com/services/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<v2:assetId>''' + str(criteria['asset_id']) + '''</v2:assetId></v2:CurrentDataItemValueCriteria>'''

		r = self.postRequest(url, headers, payload)
		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def getSourceDataItems(self, id):
		"""
		Returns the source Data Items associated with the specified source Data Item.
		"""
		self.checkParameter((id,))

		url = self.setURL("id/" + str(id) + "/sourceDataItems")

		headers = self.setHeaders(json = False)

		r = self.getRequest(url, headers)

		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def getTargetDataItems(self, id):
		"""
		Returns the source Data Items associated with the specified target Data Item.
		"""
		self.checkParameter((id,))

		url = self.setURL("id/" + str(id) + "/targetDataItems")

		headers = self.setHeaders(json = False)
	
		r = self.getRequest(url, headers)

		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def findHistoricalValues(self, **p):
		"""
		Returns the historical values of the specified Data Items.
		"""
		url = self.setURL("findHistoricalValues")

		headers = self.setHeaders(json = True)

		if True:
			payload = json.dumps(p)
		else:
			payload = \
			'''<v2:CurrentDataItemValueCriteria sortAscending="true" sortPropertyName="name" xmlns:v2="http://www.axeda.com/services/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<v2:assetId>''' + str(criteria['asset_id']) + '''</v2:assetId></v2:CurrentDataItemValueCriteria>'''

		r = self.postRequest(url, headers, payload)
		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def bulkCreate(self, c):
		"""
		Creates a new Data Item.

		@name:
		@model:
		@type:
			DIGITAL
			ANALOG
			STRING
		"""
		self.checkParameter((c,))

		TypeDataItemCollection(c)



		url = self.setURL("bulk/create")

		headers = self.setHeaders(json = False)

		if False:
			payload = json.dumps({
				"name": name,
				"type": type,
				"model": {
					"id": id,
				},
			})
		else:
			payload = \
			'''<DataItemCollection xmlns="http://www.axeda.com/services/v2">
<dataItem xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="DataItem">
<name>''' + name + '''</name><model id="''' + model + '''"/><type>''' + type + '''</type>
</dataItem></DataItemCollection>'''

		r = self.putRequest(url, headers, payload)
		if r.status_code == 200:
			return json.loads(r.content)
		else:
			return None

	def bulkDelete(self):
		pass

	def bulkSave(self):
		pass

	def bulkUpdate(self):
		pass
