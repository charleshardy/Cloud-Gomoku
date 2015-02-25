# -*- coding: utf-8 -*-

"""
General setting items:

@cloud: cloud API used
@ssl: options for the use with SSL or not
- None: use HTTP
- True: use HTTPS and verify the certificate
- False: use HTTPS but not verify the certificate
"""

cloud_configs = {
	# Settings for Axeda platform
	"Axeda": {
		"name": "windriver.axeda.com",
		"username": "windriver-es2015-team4",
		"password": "emseng1A",
		#"username": "admin",
		#"password": "windEMS11",
		#"username": "windriver",
		#"password": "windEMS11",
		"asset": "valvrave-pma1",
		"model": "es2015-Galileo-Gen2",
		"timeout": 3000,
		"ssl": None,
		"debug": True,
	},
	# Settings for Mashery API manager
	"Mashery": {
		# Available server names:
		# - ems (windriver.axeda.com)
		"name": "ems",
		"api_key": "dp62tkgsnem83hn7a6377ugu",
		"asset": "valvrave-pma1",
		"model": "es2015-Galileo-Gen2",
		# SSL must be used for Mashery API manager.
		# But requests module cannot handle certificate directly.
		# Thus we just ignore the certificate with warning like this:
		# urllib3\connectionpool.py:734: InsecureRequestWarning: Unverified
		# HTTPS request is being made. Adding certificate verification is strongly
		# advised. See: https://urllib3.readthedocs.org/en/latest/security.html
		"ssl": False,
		"debug": True,
	},
}
