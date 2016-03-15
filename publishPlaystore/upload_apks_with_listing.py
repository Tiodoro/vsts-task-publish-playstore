#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License");
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

"""Uploads apk to alpha track and updates its listing properties."""

import mimetypes
import os
mimetypes.add_type("application/vnd.android.package-archive", ".apk")

import argparse
import sys
from apiclient.discovery import build
import httplib2
from oauth2client import tools
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client import client

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('package_name',
                       help='The package name. Example: com.android.sample')
argparser.add_argument('apk_file',
                       nargs='?',
                       default='test.apk',
                       help='The path to the APK file to upload.')
argparser.add_argument('-language',
                       nargs='?',
                       default='en-US',
                       help='The language to update the listing.')
argparser.add_argument('-jsonFile',
                       nargs='?',
                       default='key.json',
                       help='JSON File')
argparser.add_argument('-message',
                       nargs='?',
                       default='Apk recent changes',
                       help='Message')
argparser.add_argument('-track',
                       nargs='?',
                       default='alpha',
                       help='Track')


def main(argv):
  # Process flags and read their values.
  
  parent_parsers = [tools.argparser]
  
  parent_parsers.extend([argparser])
  parser = argparse.ArgumentParser( 
      description=__doc__, 
      formatter_class=argparse.RawDescriptionHelpFormatter, 
      parents=parent_parsers) 
  flags = parser.parse_args(argv[1:]) 
  
  package_name = flags.package_name
  apk_file = flags.apk_file
  language = flags.language
  jsonFile = flags.jsonFile
  message = flags.message
  track = flags.track
  
  # Authenticate and construct service.
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      jsonFile,
      scopes=['https://www.googleapis.com/auth/androidpublisher']
  )
  
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build('androidpublisher', 'v2', http=http)

  try:
    edit_request = service.edits().insert(body={}, packageName=package_name)
    result = edit_request.execute()
    edit_id = result['id']

    apk_response = service.edits().apks().upload(
        editId=edit_id,
        packageName=package_name,
        media_body=apk_file).execute()

    print ('Version code ', apk_response['versionCode'], ' has been uploaded')

    track_response = service.edits().tracks().update(
        editId=edit_id,
        track=track,
        packageName=package_name,
        body={u'versionCodes': [apk_response['versionCode']]}).execute()

    print ('Track ', track_response['track'], ' is set for version code(s) ', str(track_response['versionCodes']))

    listing_response = service.edits().apklistings().update(
        editId=edit_id, packageName=package_name, language=language,
        apkVersionCode=apk_response['versionCode'],
        body={'recentChanges': message}).execute()

    print ('Listing for language ', listing_response['language'], ' was updated.')

    commit_request = service.edits().commit(
        editId=edit_id, packageName=package_name).execute()

    print ('Edit "', commit_request['id'], '" has been committed')

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
