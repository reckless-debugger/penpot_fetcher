from http.client import HTTPSConnection

from dotenv import load_dotenv
from os import getenv

import sys
import time
import json

class HTTPS_Request():
	def __init__(self, host, method, url, headers, payload=None):
		self.host: str = host
		self.method: str = method
		self.url: str = url
		self.headers: dict = headers
		self.payload: dict = payload #json.dumps(None) == 'null', how the https client handles that ?

		self.https_client = HTTPSConnection(host)

	def main(self)-> None:
		self.load(self.parse(self.send()))

	def send(self)-> str:
		self.https_client.request(method=self.method, url=self.url,body=json.dumps(self.payload), headers=self.headers)

		response = self.https_client.getresponse()
		self.https_client.close()

		""" if not response.status==200:
			raise Exception(f'Request failed : {response.status} {response.reason}') """

		return response.read()

	def parse(self, raw_response)-> list:
		match self.headers['Accept']:
			case 'application/json':
				try:
					parsed_response: list = json.loads(raw_response.decode('utf-8'))
				except Exception as e:
					print(f'error : {e}')
					sys.exit()

			case 'application/transit+json':
				pass

			case _:
				pass

		return parsed_response

	def load(self, parsed_response)-> None: #default loading implementation
		with open('load.txt', 'a') as file:
			file.write(str(parsed_reponse)+'\n')

if __name__ == '__main__':
	load_dotenv()
	token: str = getenv('ACCESS_TOKEN')
	email: str = getenv('ACCOUNT_EMAIL')
	password: str = getenv('ACCOUNT_PWD')
    

	host='design.penpot.app'
	headers: dict = {
			'Authorization': f'Token {token}',
			'Accept': 'application/json'
			}

	#rpc_methods = {path:payload, ...}
	rpc_methods: dict = {
		'/api/rpc/command/login-with-password':{
			'email': email,
			'password': password
		},
		'/api/rpc/command/get-profile':{}
	}


	for path, payload in rpc_methods.items():
		handler = HTTPS_Request(
			host=host,
			method='POST',
			url=path,
			headers=headers,
			payload=payload
		)

		handler.main()

		time.sleep(1)
