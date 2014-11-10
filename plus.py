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

# me, myself and i
  
    person = service.people().get(userId='me').execute(http=http)
    print "Welcome %s" % person['displayName']
#    print
#    print "%-040s -> %s" % ("[Activitity ID]", "[Content]")

    # Don't execute the request until we reach the paging loop below
#    request = service.activities().list(
#        userId=person['id'], collection='public')
    # Loop over every activity and print the ID and a short snippet of content.
#    while ( request != None ):
#      activities_doc = request.execute()
#      for item in activities_doc.get('items', []):
#        print '%-040s -> %s' % (item['id'], item['object']['content'][:30])

#      request = service.activities().list_next(request, activities_doc)

# activities

    # This sample assumes a client object has been created.
    # To learn more about creating a client, check out the starter:
    #  https://developers.google.com/+/quickstart/python

    try:
      _keyword = sys.argv[1].replace(' ','+')
      #_access_token = googlepluscredentials.ACCESS_TOKEN
      _path = sys.argv[2]
      #tell computer where to put CSV
      outfile_path=_path + '/googleplus_stream_%s_%i%i%i%i%i.csv' % (_keyword,now.year,now.month,now.day,now.hour,now.minute)
      # open it up, the w means we will write to it
      writer = csv.writer(open(outfile_path, 'w'))
      #create a list with headings for our columns
      headers = ['source','published','title','url','type','id','actor','image','','','','etag','','','','','','content','kind','weblink','','objecttype']
      #write the row of headings to our CSV file
      writer.writerow(headers)
    except IndexError:
      print 'usage: python plus.py <keyword> <path>'
      sys.exit()
    except IOError:
      print 'Path doesn\'t exist !'
      sys.exit()

    activities_resource = service.activities()
    activities_document = activities_resource.search(maxResults=20,orderBy='best',prettyPrint='true',query=_keyword).execute()
    activities = []
    npt = None

    if 'items' in activities_document:
      activities = activities_document[ 'items' ]
      print "Retrieved %d activities" % len(activities_document['items'])
    sleep(2)

    npt = activities_document['nextPageToken']

    while ( npt != None ):
      try:
        activities_document = activities_resource.search(maxResults=20,orderBy='best',prettyPrint='true',pageToken=npt,query=_keyword).execute()
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
        row.append(unicode(item['provider']['title']).encode('utf-8'))
        row.append(item['published'])
        row.append(unicode(item['title']).encode('utf-8'))
        row.append(item['url'])
        row.append(item['verb'])
        row.append(item['actor']['id'])
        row.append(unicode(item['actor']['displayName']).encode('utf-8'))
        row.append(item['actor']['image']['url'])
        try:
          row.append(unicode(item['actor']['name']['familyName']).encode('utf-8'))
          row.append(unicode(item['actor']['name']['givenName']).encode('utf-8'))
        except KeyError:
          row.append('')
          row.append('')
        row.append(item['actor']['url'])
        try:
          row.append(unicode(item['address']).encode('utf-8'))
        except KeyError:
          row.append('')
        #print 'annotation: ' + item['annotation']
        #print 'crosspostSource: ' + item['crosspostSource']
        row.append(unicode(item['etag']).encode('utf-8'))
        try:
          row.append(item['geocode'])
        except KeyError:
          row.append('')
        row.append(item['id'])
        row.append(item['kind'])
        #print 'actor: ' + item['object']['actor']['displayName']
        #print 'displayName: ' + unicode(item['object']['attachments'][0]['displayName']).encode('utf-8')
        try:
          row.append(unicode(item['object']['attachments'][0]['content']).encode('utf-8'))
        except KeyError:
          row.append('')
        try:
          row.append(item['object']['attachments'][0]['image']['url'])
        except KeyError:
          row.append('')
        try:
          row.append(item['object']['attachments'][0]['objectType'])
        except KeyError:
          row.append('')
        try:
          row.append(item['object']['attachments'][0]['url'])
        except KeyError:
          row.append('')
        row.append(unicode(item['object']['content']).encode('utf-8'))
        row.append(item['object']['objectType'])
        try:
          row.append(item['placeId'])
          row.append(unicode(item['placeName']).encode('utf-8'))
        except KeyError:
          row.append('')
          row.append('')
        #print '-----------'
        writer.writerow(row)

# people search

    #people_resource = service.people()
    #people_document = people_resource.search( \
    #maxResults=10,query='benjamin engeli').execute()

    #if 'items' in people_document:
    #  print 'got page with %d' % len( people_document['items'] )
    #  for person in people_document['items']:
    #    print person['id'], person['displayName']

  except AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")

if __name__ == '__main__':
  main(sys.argv)
