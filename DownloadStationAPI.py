import sys
import logging
logging.basicConfig(level=logging.DEBUG,stream=sys.stdout)
import time
import requests
import json


class DownloadStationAPI():

    def __init__(self, host=None, username=None, password=None):

        self.name = 'DownloadStation'
        self.username = username
        self.password = password
        self.host = host

        self.url = None
        self.response = None
        self.auth = None
        self.last_time = time.time()
        self.session = requests.session()

        self.url = self.host + 'webapi/DownloadStation/task.cgi'
        self._get_auth()

    def _get_auth(self):

        auth_url = self.host + 'webapi/auth.cgi?api=SYNO.API.Auth&version=2&method=login&account=' + self.username + '&passwd=' + self.password + '&session=DownloadStation&format=sid'
        logging.debug(auth_url)
        try:
            self.response = self.session.get(auth_url)
            self.auth = json.loads(self.response.text)['data']['sid']
        except:
            return None

        return self.auth

    def add_uri(self, url, destination=None):

        data = {'api': 'SYNO.DownloadStation.Task',
                'version': '1', 'method': 'create',
                'session': 'DownloadStation',
                '_sid': self.auth,
                'uri': url,
                'destination': destination
                }
        logging.debug(data)
        logging.debug(self.url)
        self.response = self.session.post(url=self.url, data=data)
        return json.loads(self.response.text)

    def get_status(self):

        data = {'api': 'SYNO.DownloadStation.Task',
                'version': '1', 'method': 'list',
                'additional': 'detail,file',
                'session': 'DownloadStation',
                '_sid': self.auth,
                }
        self.response = requests.post(url=self.url, data=data)

        return json.loads(self.response.text)



    def delete(self,id):
        data = {'api': 'SYNO.DownloadStation.Task',
                'version': '1', 'method': 'delete',
		'_sid': self.auth,
		'id': id
		}
        logging.debug(self.url)
        logging.debug(data)
        self.response = requests.delete(url=self.url, data=data)
        logging.debug(json.dumps(self.response.text))
        return json.loads(self.response.text)
