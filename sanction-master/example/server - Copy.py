#!/usr/bin/env python
# vim: set ts=4 sw=4 et:

import logging
import sys, os, time
import urllib
import urllib2
import requests
import json
import pprint
import sqlite3
from DatabaseManager import DatabaseManager




try:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from ConfigParser import ConfigParser
    from urlparse import urlparse, urlsplit, urlunsplit, parse_qsl
    from urllib import urlencode
    from urllib2 import Request
    from io import BytesIO 
except ImportError:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from configparser import ConfigParser
    from urllib.parse import (urlparse, parse_qsl, urlencode,
        urlunsplit, urlsplit)
    from io import BytesIO 
    from urllib.request import Request

from gzip import GzipFile
from json import loads

# so we can run without installing
sys.path.append(os.path.abspath('../'))

from sanction import Client, transport_headers

ENCODING_UTF8 = 'utf-8'
ENCODING_UTF16LE = 'utf-16le'
access_token = 'None'
createDb = sqlite3.connect('key.db')
queryCurs = createDb.cursor()
queryCurs.execute('''CREATE TABLE if not exists userinfo
    (key TEXT, expires TEXT)''')

def createInfo(key, expires):
    #createTable()
    queryCurs.execute('''INSERT INTO userinfo (key,expires)
    VALUES (?,?)''',(key,expires))
    createDb.commit()

def get_config():
    config = ConfigParser({}, dict)
    config.read('example.ini') 

    c = config._sections['sanction']
    if '__name__' in c:
        del c['__name__']

    if 'http_debug' in c:
        c['http_debug'] = c['http_debug'] == 'true'

    return config._sections['sanction']


logging.basicConfig(format='%(message)s')
l = logging.getLogger(__name__)
config = get_config()


class Handler(BaseHTTPRequestHandler):
    route_handlers = {
        '/': 'handle_root',
        '/oauth2/jawbone': 'handle_jawbone',
        '/login/jawbone': 'handle_jawbone_login',
        '/get_data': 'get_data',
        '/logout': 'logout',
    }
    
    def do_GET(self):
        url = urlparse(self.path)
        if url.path in self.route_handlers:
            getattr(self, self.route_handlers[url.path])(
            dict(parse_qsl(url.query)))
        else:
            self.send_response(404)

    def do_POST(self):
        self.send_response(200)
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        print post_body
        #Hub = Harmony.Bridge()
        if 'enter_sleep_mode' in post_body:
            print "entered sleep"
        elif 'exit_sleep_mode' in post_body:
            print "exit sleep"


    def success(func):
        def wrapper(self, *args, **kwargs):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.log_message(self.path)
            self.end_headers()
            return func(self, *args, **kwargs)
        return wrapper

    @success
    def handle_root(self, data):
        self.wfile.write('''
            login with:
            <a href='/oauth2/jawbone'>Jawbone</a>,
            <a href='/get_data'>Get Data</a>,
            <a href='/logout'>Log Out</a>,
        '''.encode(ENCODING_UTF8))


    def _gunzip(self, data):
        s = BytesIO(data)
        gz = GzipFile(fileobj=s, mode='rb')
        return gz.read()


    def dump_response(self, data):
        for k in data:
            self.wfile.write('{0}: {1}<br>'.format(k,
                data[k]).encode(ENCODING_UTF8))

    def dump_client(self, c):
        for k in c.__dict__:
            self.wfile.write('{0}: {1}<br>'.format(k,
                c.__dict__[k]).encode(ENCODING_UTF8))
        self.wfile.write('<hr/>'.encode(ENCODING_UTF8))



    def handle_jawbone(self, data):
        self.send_response(302)
        c = Client(auth_endpoint='https://jawbone.com/auth/oauth2/auth',
            client_id='nEXyCKO3F3s')
        self.send_header('Location', c.auth_uri(
            scope='basic_read extended_read location_read friends_read mood_read mood_write move_read sleep_read sleep_write generic_event_read generic_event_write',
            redirect_uri='http://localhost/login/jawbone'))
        self.end_headers()

    @success
    def handle_jawbone_login(self, data):
        c = Client(token_endpoint='https://jawbone.com/auth/oauth2/token',
            client_id='nEXyCKO3F3s',
            client_secret='c9a66fc619ccb0e7c2c4e90e59200dfba8aea5de',
            token_transport=transport_headers)
        c.request_token(grant_type='authorization_code',code=data['code'])

        #createInfo(c.access_token,c.token_expires)
        query = DatabaseManager('key.db')
        #maybe check if table doesn't exist and create it in DBMR__init__)
        query.updateInfo("UPDATE userinfo SET key = ?, expires = ?",c.access_token,c.token_expires)
        del query

       

             

        self.dump_client(c)
        return

        
        
        


    #@success
    def get_data(self, data):
        self.send_response(302)
        #access database
        query = DatabaseManager("key.db")
        query.query('SELECT key FROM userinfo')
        for row in query.cur:
            access_token = str(row[0])
        del query

        #make request to jawbone api                
        req = urllib2.Request('https://jawbone.com/nudge/api/users/@me/moves')
        req.add_header('content-type', 'application/json')
        req.add_header('Authorization', 'Bearer ' + access_token)
        res = urllib2.urlopen(req)

        

    def logout(self, data):
        self.send_response(302)
        
        
      


if __name__ == '__main__':
    l.setLevel(1)
    server_address = ('', 80)
    server = HTTPServer(server_address, Handler)
    l.info('Starting server on %sport %s \nPress <ctrl>+c to exit' % server_address)
    server.serve_forever()

