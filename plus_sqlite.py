# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple command-line sample for the Google+ API.

Command-line application that retrieves the users latest content and then adds a new entry.

Usage:
  $ python plus.py

You can also get help on all the command-line flags the program understands
by running:

  $ python plus.py --help

To get detailed log output run:

  $ python plus.py --logging_level=DEBUG
"""

import gflags
import httplib2
import urllib2
import logging
import os
import pprint
import sys
import time
import datetime
now = datetime.datetime.now()
from time import sleep
import json
import csv

import apiclient
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

FLAGS = gflags.FLAGS

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = 'client_secrets.json'

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the APIs Console <https://code.google.com/apis/console>.

""" % os.path.join(os.path.dirname(__file__), CLIENT_SECRETS)

# Set up a Flow object to be used if we need to authenticate.
FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/plus.me',
    message=MISSING_CLIENT_SECRETS_MESSAGE)

# The gflags module makes defining command-line options easy for
# applications. Run this program with the '--help' argument to see
# all the flags that it understands.
gflags.DEFINE_enum('logging_level', 'ERROR',
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'Set the level of logging detail.')

import sqlite3
conn = sqlite3.connect('demo.db')
conn.text_factory = str
c = conn.cursor()

def main(argv):
    # Let the gflags module process the command-line arguments
    try:
        argv = FLAGS(argv)
    except gflags.FlagsError, e:
        print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], FLAGS)
        sys.exit(1)

    # Set the logging according to the command-line flag
    logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))

    # If the Credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # Credentials will get written back to a file.
    storage = Storage('plus.dat')
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run(FLOW, storage)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build("plus", "v1", http=http)

    try:
        # create table if not exists
        table = "CREATE TABLE IF NOT EXISTS stream (id INTEGER PRIMARY KEY AUTOINCREMENT,provider TEXT, published TEXT, title TEXT, url TEXT, verb TEXT, actor_id TEXT, actor_displayname TEXT, actor_image TEXT, actor_familyname TEXT, actor_givenname TEXT, actor_url TEXT, address TEXT, etag TEXT, geocode TEXT, post_id TEXT, post_kind TEXT, attachment TEXT, attachment_image_url TEXT, attachment_objecttype TEXT,attachment_url TEXT,content TEXT,object_type TEXT,place_id TEXT,place_name TEXT)"
        c.execute(table)
        #_keyword = sys.argv[1].replace(' ','+')
        _keyword = 'demo'
        #headers = ['source','published','title','url','type','id','actor','image','','','','etag','','','','','','content','kind','weblink','','objecttype']
      
        activities_resource = service.activities()
        activities_document = activities_resource.search(maxResults=20,orderBy='recent',prettyPrint='true',query=_keyword).execute()
        activities = []
        dict = []
        npt = None

        if 'items' in activities_document:
            activities = activities_document[ 'items' ]
            print "Retrieved %d activities" % len(activities_document['items'])
            sleep(2)

            npt = activities_document['nextPageToken']

            while ( npt != None ):
                try:
                    activities_document = activities_resource.search(maxResults=20,orderBy='recent',prettyPrint='true',pageToken=npt,query=_keyword).execute()
                    if 'items' in activities_document:
                        activities += activities_document['items']
                        print "Retrieved %d more activities" % len(activities_document['items'])
                    if len(activities_document['items']) == 0:
                        break
                    npt = activities_document['nextPageToken']
                    sleep(2)
                except apiclient.errors.HttpError:
                    break

        if not 'nextPageToken' in activities_document or activities_document['nextPageToken'] == npt:
            #break
            print "---Done"

        if len(activities) > 0:
            for item in activities:
                row = []
                # 1 provider
                row.append(unicode(item['provider']['title']).encode('utf-8'))
                # 2 published
                row.append(item['published'])
                # 3 title
                row.append(unicode(item['title']).encode('utf-8'))
                # 4 title
                row.append(item['url'])
                # 5 verb
                row.append(item['verb'])
                # 6 actor id
                row.append(item['actor']['id'])
                # 7 actor displayname
                row.append(unicode(item['actor']['displayName']).encode('utf-8'))
                # 8 actor image url
                row.append(item['actor']['image']['url'])
                try:
                    # 9 actor familyname
                    row.append(unicode(item['actor']['name']['familyName']).encode('utf-8'))
                    # 10 actor givenname
                    row.append(unicode(item['actor']['name']['givenName']).encode('utf-8'))
                except KeyError:
                    # 9 actor familyname
                    row.append('')
                    # 10 actor givenname
                    row.append('')
                # 11 actor url
                row.append(item['actor']['url'])
                try:
                    # 12 address
                    row.append(unicode(item['address']).encode('utf-8'))
                except KeyError:
                    # 12 address
                    row.append('')
                #print 'annotation: ' + item['annotation']
                #print 'crosspostSource: ' + item['crosspostSource']
                # 13 etag
                row.append(unicode(item['etag']).encode('utf-8'))
                try:
                    # 14 geocode
                    row.append(item['geocode'])
                except KeyError:
                    # 14 geocode
                    row.append('')
                # 15 id
                row.append(item['id'])
                # 16 kind
                row.append(item['kind'])
                #print 'actor: ' + item['object']['actor']['displayName']
                #print 'displayName: ' + unicode(item['object']['attachments'][0]['displayName']).encode('utf-8')
                try:
                    # 17 object attachment
                    row.append(unicode(item['object']['attachments'][0]['content']).encode('utf-8'))
                except KeyError:
                    # 17 object attachment
                    row.append('')
                try:
                    # 18 object attachment image
                    row.append(item['object']['attachments'][0]['image']['url'])
                except KeyError:
                    # 18 object attachment image
                    row.append('')
                try:
                    # 19 object attachment objecttype
                    row.append(item['object']['attachments'][0]['objectType'])
                except KeyError:
                    # 19 object attachment objecttype
                    row.append('')
                try:
                    # 20 object attachment url
                    row.append(item['object']['attachments'][0]['url'])
                except KeyError:
                    # 20 object attachment url
                    row.append('')
                # 21 object content
                row.append(unicode(item['object']['content']).encode('utf-8'))
                # 22 object objecttype
                row.append(item['object']['objectType'])
                try:
                    # 23 placeId
                    row.append(item['placeId'])
                    # 24 placeName
                    row.append(unicode(item['placeName']).encode('utf-8'))
                except KeyError:
                    # 23 placeId
                    row.append('')
                    # 24 placeName
                    row.append('')
                #print '-----------'
                #writer.writerow(row)
                dict.append(row)
                #print dict

        sql = "INSERT INTO stream (provider, published, title, url, verb, actor_id, actor_displayname, actor_image, actor_familyname, actor_givenname, actor_url, address, etag, geocode, post_id, post_kind, attachment, attachment_image_url, attachment_objecttype,attachment_url,content,object_type,place_id,place_name) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)" #% _event_id
        c.executemany(sql, dict)

        # remove duplicate items from table
        dups = "DELETE FROM stream WHERE id NOT IN (SELECT MAX(id) FROM stream GROUP BY post_id);" #% (_object_id,_object_id)
        c.execute(dups)

        conn.commit()
        conn.close()    

    except AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
          "the application to re-authorize")

if __name__ == '__main__':
  main(sys.argv)
