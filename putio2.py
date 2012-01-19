# -*- coding: utf-8 -*-
"""
A python wrapper for put.io APIv2

https://github.com/putdotio/putio-apiv2-python


Usage:

# TODO write usage

"""

import json
import logging
import requests
from urllib import urlencode

logger = logging.getLogger(__name__)

API_URL = 'https://put.io/v2'
ACCESS_TOKEN_URL = 'https://put.io/v2/oauth2/access_token'
AUTHENTICATION_URL = 'https://put.io/v2/oauth2/authenticate'


class AuthHelper(object):
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_url = redirect_uri
    
    def get_authentication_url(self):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.callback_url
        }
        query_str = urlencode(query)
        return AUTHENTICATION_URL + "?" + query_str
    
    def get_access_token(self, code):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': self.callback_url,
            'code': code
        }
        r = requests.get(ACCESS_TOKEN_URL, params=params)
        d = json.loads(r.content)
        return d['access_token']


class Client(object):
    def __init__(self, access_token):
        self.access_token = access_token
        
        attributes = {'client': self}
        self.File = type('File', (_File,), attributes)
        #self.Transfer = type('Transfer', (_Transfer,), attributes)
    
    def request(self, path, method='GET', params=None, data=None, as_dict=True):
        if not params:
            params = {}
        params['oauth_token'] = self.access_token
        
        url = API_URL + path
        logger.debug('url: %s', url)
        r = requests.request(method, url, params=params, data=data, allow_redirects=True)
        logger.debug('response: %s', r)
        if not as_dict:
            return r.content
        
        logger.debug('content: %s', r.content)
        r = json.loads(r.content)
        if r['status'] == 'ERROR':
            raise Exception(r['error_type'])
        return r


class _BaseResource(object):
    def __init__(self, resource_dict):
        self.__dict__.update(resource_dict)
        
    def __str__(self):
        return self.name

    def __repr__(self):
        # shorten name for display
        name = self.name[:17] + '...' if len(self.name) > 20 else self.name
        return 'File(%s, "%s")' % (self.id, name)


class _File(_BaseResource):
    @classmethod
    def list(cls, parent_id=0):
        d = cls.client.request('/files/list', params=dict(parent_id=parent_id))
        files = d['files']
        files = [cls(f) for f in files]
        ids = [f.id for f in files]
        return dict(zip(ids, files))
    
    def download(self):
        return self.client.request('/files/%s' % self.id, as_dict=False)

    def delete(self):
        return self.client.request('/files/%s/delete' % self.id)
