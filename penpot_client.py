'''
HTTPS Client fetching, decoding, then loading data retrieved from the Penpot's RPC API.

Detailed process :
	- Retrieve login tokens
	- Log in
	- Grab Session's cookie
	- Send specific requests concurrently (via Threads)
	- Parse fetched data
	- Load it within content.json

to-do : implement logging, more error handling, threading

Notes : only the dotenv module is third-party, everything else is built-in, because of
fine-grained needs of request customization and cookie handling.
'''


from http.client import HTTPSConnection
import threading

from dotenv import load_dotenv
from os import getenv

import re
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
		'''Sends request to the provided URI, checks for response correctness, then return response's headers and raw content'''

		self.https_client.request(method=self.method, url=self.url, body=json.dumps(self.payload), headers=self.headers)

		response = self.https_client.getresponse()
		self.https_client.close()

		if not 200 <= response.status <= 299:
			raise Exception(f'''Request Failed : \n- Status : {response.status}
			\n- Reason : {response.reason}
			\n- Raw response : {response.read()}''')

		return [response.getheader('Set-Cookie'), response.read()]
		
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
	email: str = getenv('ACCOUNT_EMAIL')
	password: str = getenv('ACCOUNT_PWD')
	
	# Requests initial composure
	host='design.penpot.app'
	headers={
		"Content-Type": "application/json",
		"Accept": "application/json",
		"User-Agent": "PenpotDevClient/1.0"
		}

	#Setting up login handler
	login_handler = RequestHandler(
		host=host,
		method='POST',
		url='/api/rpc/command/login-with-password',
		headers=headers,
		payload={
		"email": email,
		"password": password
		}
	)

	try:
		#Logging in
		response = login_handler.fetch()
	except Exception as e:
		#Case logging fails
		print(e)
		sys.exit()
	else:
		#Case logging succeeds
		#Grab auth-token from the Session's cookie and add it to the headers
		auth_token =  re.search(r"(?<=auth-token=)[^;|)]+", response[0]).group()
		headers: dict = headers | {"Authorization": f"Token {auth_token}"}

		#Threaded RPC methods execution
		rpc_methods: dict = {
			'/api/rpc/command/get-profile':{}
		}

		#Implement threading