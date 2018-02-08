#!/usr/bin/env python

# Credits :
# Richard Hailstone - Redhat : rhailsto@redhat.com


import json
import os
import urllib2
import urllib
import base64
import sys
import ssl
#import csv
import re
import argparse
import ConfigParser
import time

from six import iteritems
#from optparse import OptionParser

class error_colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class InsightsInventory(object):

    def return_meta(self):
      return {
        'hostvars': {
         }
      }

    def base_inventory(self):
      return {
          'servergroup': {
              'hosts': [],
               'vars': {
                }
          },
          '_meta': {
              'hostvars': {
              }
          }
      }

    def __init__(self):
        parser = argparse.ArgumentParser(description='Insights Inventory', epilog='Epilogue')
        parser.add_argument( '-l', '--list', action='store_true', help='gives out a list')
        args = parser.parse_args()
        insights_url = 'access.redhat.com'
        insights_uri = '/r/insights/v2/systems'
        VERBOSE = False
        self.login = os.environ.get("INSIGHTS_USERNAME")
        self.password = os.environ.get("INSIGHTS_PASSWORD")
        groups={}
        # This is the group name that will show up in the Tower inventory and also which marks the
        # section that we are interested in within the ini file. In future we will honour the group
        # definition within insights.

        section_name = 'insights'

        if section_name not in groups:
          groups[section_name] = set()
        
        systemdata = []

        try:
          url = "https://" + insights_url + insights_uri
          request = urllib2.Request(url)
          if VERBOSE:
             print "=" * 80
             print "[%sVERBOSE%s] Connecting to -> %s " % (error_colors.OKGREEN, error_colors.ENDC, url)
          base64string = base64.encodestring('%s:%s' % (self.login, self.password)).strip()
          request.add_header("Authorization", "Basic %s" % base64string)
          request.add_header("Content-Type", "application/json")
          requestresult = urllib2.urlopen(request)
          jsonresult = json.loads(requestresult.read().decode('utf-8'))
          systemdata += jsonresult['resources']

        except urllib2.URLError, e:
          print "Error: cannot connect to the API: %s" % (e)
          print "Check your URL & try to login using the same user/pass via the WebUI and check the error!"
          sys.exit(1)
        except Exception, e:
          print "FATAL Error - %s" % (e)
          sys.exit(2)

        inv_exclude = re.compile("some.example.com|other.example.com")

        # you can set a value in the re.match below with a hostname pattern. 
        # Limits what gets returned from insights.
        # To do - import group membership based on that defined from insights

        for system in systemdata:
          #m = re.match("(^rjhins.*)" ,system["hostname"])
          m = re.match("(^.*)" ,system["hostname"])
          if inv_exclude.search(system["hostname"]):
            continue
          if m and system['isCheckingIn'] == True:
            groups[section_name].add(system["hostname"])

        final = dict([(k, list(s)) for k, s in iteritems(groups)])

        # _meta tag prevents Ansible from calling this script for each server with --host
        final["_meta"] = self.return_meta()
        print(json.dumps(final))
        sys.exit(0)


InsightsInventory()
