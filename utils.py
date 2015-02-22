# -*- coding: utf-8 -*-

import requests
import json
from xml.etree import ElementTree
import mashery_api

debug = False

def get(url, headers, payload = None, ssl = False):
	if payload:
		if not "?" in url:
			parameters = "?"
		elif url[-1] != "&":
			parameters = "&"
		else:
			parameters = ""

		for k, v in payload.items():
			parameters += k + "=" + v + "&"

		url += parameters

	if debug:
		print("GET %s" % url)
		print("  Headers: %s" % headers)
		print("  SSL: %s" % repr(ssl))

	if not url.startswith("https"):
		r = requests.get(url, headers = headers)
	else:
		r = requests.get(url, headers = headers, verify = ssl)

	if debug:
		print("  Status: %s" % r.status_code)
		print("  Headers: %s" % r.headers)
		print("  Content: %s" % r.content)

	return r

def post(url, headers, payload, ssl = None):
	if debug:
		print("POST %s" % url)
		print("  Headers: %s" % headers)
		print("  Payload: %s" % payload)
		print("  SSL: %s" % repr(ssl))

	if not url.startswith("https"):
		r = requests.post(url, headers = headers, data = payload)
	else:
		r = requests.post(url, headers = headers, data = payload, verify = ssl)

	if debug:
		print("  Status: %s" % r.status_code)
		print("  Headers: %s" % r.headers)
		print("  Content: %s" % r.content)

	return r

def put(url, headers, payload, ssl = None):
	if debug:
		print("PUT %s" % url)
		print("  Headers: %s" % headers)
		print("  Content: %s" % payload)
		print("  SSL: %s" % repr(ssl))

	if not url.startswith("https"):
		r = requests.put(url, headers = headers, data = payload)
	else:
		r = requests.put(url, headers = headers, data = payload, verify = ssl)

	if debug:
		print("  Status: %s" % r.status_code)
		print("  Headers: %s" % r.headers)
		print("  Content: %s" % r.content)

	return r

def delete(url, headers, ssl = False):
	if debug:
		print("DELETE %s" % url)
		print("  Headers: %s" % headers)
		print("  SSL: %s" % repr(ssl))

	if not url.startswith("https"):
		r = requests.delete(url, headers = headers)
	else:
		r = requests.delete(url, headers = headers, verify = ssl)

	if debug:
		print("  Status: %s" % r.status_code)
		print("  Headers: %s" % r.headers)
		print("  Content: %s" % r.content)

	return r

def parse_json(json, key = None):
	"""
	TODO
	"""
	pass

def parse_xml(xml, key = None, name_space = None):
	root = ElementTree.fromstring(xml)
	if key == None:
		ElementTree.dump(root)

	if key:
		if name_space:
			key = '{' + name_space + '}' + key
		return root.find(key).text
