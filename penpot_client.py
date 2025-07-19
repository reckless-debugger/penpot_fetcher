'''
HTTPS Client fetching, decoding, then loading data retrieved from the Penpot's RPC API.

Notes : only the dotenv module is third-party, everything else is built-in, because of
fine-grained needs of request customization and cookie handling.
'''


from http.client import HTTPSConnection
import threading

from dotenv import load_dotenv
from os import getenv

import sys
import time
import json

class RequestHandler():
	'''Simple HTTPS request handler fetching, decoding then loading data from any endpoint.'''
	
	def __init__(self, host, method, url, headers, payload=None):
		self.host: str = host
		self.method: str = method
		self.url: str = url
		self.headers: dict = headers
		self.payload: dict = payload #json.dumps(None) == 'null', how the https client handles that ?

		self.https_client = HTTPSConnection(host)
		
	def fetch(self)-> list:
		'''fetch -> [response.status, response.reason, response.read()]'''
		self.https_client.request(method=self.method, url=self.url, body=json.dumps(self.payload), headers=self.headers)

		response = self.https_client.getresponse()
		self.https_client.close()

		""" if not response.status==200:
			raise Exception(f'Request failed : {response.status} {response.reason}') """

		return [response.status, response.reason, response.getheaders(), response.read()]
		
	def decode(self, raw_response)-> list: #OBSOLETE
		match self.headers['Accept']:
			case 'application/json':
				try:
					parsed_response: list = json.loads(raw_response.decode('utf-8'))
				except Exception as e:
					print(f'error : {e}')
					sys.exit()

			case 'application/transit+json':
				pass #add transit decoder

			case _:
				pass

		return parsed_response
		
	def load(self, parsed_response)-> None: #OBSOLETE
		with open('data.txt', 'a') as file:
			file.write(str(parsed_reponse)+'\n')

if __name__ == '__main__':
	# Tokens retrieval
	load_dotenv()
	token: str = getenv('ACCESS_TOKEN')
	email: str = getenv('ACCOUNT_EMAIL')
	password: str = getenv('ACCOUNT_PWD')
	
	# Requests composure  
	host='design.penpot.app'
	headers: dict = {
			'Authorization': f'Token {token}',
			'Accept': 'application/json',
			'User-Agent':''
			}

	#Logging in
	login_method: dict = {
		'/api/rpc/command/login-with-password':{
			"email": email,
			"password": password
		}}

	for path, payload in login_method.items():
		print(path, payload, sep='\n')
		login_handler = RequestHandler(
			host=host,
			method='POST',
			url=path,
			headers={
				'Content-Type': 'application/json',
				'Accept': 'application/json',
				"User-Agent": "PenpotDevClient/1.0"
				},
			payload=payload
		)

	response = login_handler.fetch()

	print(response)

	

	#Threaded RPC methods execution
	rpc_methods: dict = {
		'/api/rpc/command/get-profile':{}
	}

	#Implement threading