#!/usr/bin/env python

import sys
from sys import version

setup_param = {
    'name'            :'WebSmsComToolkit',
    'version'         : '1.0.0',
    'py_modules'      : ['WebSmsComToolkit'],
    'url'             : 'http://websms.com/',
    'download_url'    : 'http://websms.com/entwickler/skriptsprachen/python-toolkit',
    'author'          : "Gerd Reifenauer",
    'author_email'    : "gerd.reifenauer@ut11.net",
    'description'     : 'Websms.com Toolkit to send SMS messages',
    'long_description':  """This script uses the json/simplejson module to send data to the WebSms.com API.
Will use json module if available or requires simplejson as dependency""".strip(),
    'classifiers'     : [ 'Development Status :: 4 - Beta',
                          'License :: OSI Approved :: MIT License',
                          'Programming Language :: Python',
                          'Intended Audience :: Developers',
                          'Intended Audience :: System Administrators',
                          'Intended Audience :: Telecommunications Industry',
                          'Operating System :: OS Independent',
                          'Topic :: Communications',
                          'Topic :: Internet',
                          'Topic :: Software Development',
                        ],
}

if 'install' in sys.argv:
  _has_json = False
  _has_ssl = False
  
  try:
    import json
    _has_json = True
  except ImportError:
    try:
      import simplejson
      _has_json = True
    except ImportError:
      _has_json = False
  
  try:
    import ssl
    _has_ssl = True
  except ImportError:
    _has_ssl = False
  
  if version < '2.4':
    print "\n!!! Python below version 2.4 is not officially supported.!!!"
  
  if (not _has_ssl or not _has_json):
    print "------------------------------------------------------------"
    if (not _has_ssl):
      print """
 o  SSL support is missing from your installation of python! (module 'ssl')\n"""
      
    if (not _has_json):
      print """
 o  JSON support is missing from your installation of python!"""
      if (version < '2.6'):
        print "\n You will need to install simplejson",
        #simplejson (>=2.2)
      if (version >='2.4' and version < '2.5'):
        print " v2.1.0"
        #simplejson (=2.1)
      if (version < '2.4'):
        print " v2.0.0"
        #simplejson (>=2.2)
        print "\n or some other json encoder/decoder and overwrite the\n WebSmsComToolkit.JsonWrapper class"
      
    print """
------------------------------------------------------------"""
  

from distutils.core import setup

if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(**setup_param)

#'requires-dist'        : ["simplejson (=2.0); python_version == '2.3' or python_version == '2.2'",
#                         "simplejson (=2.1); python_version == '2.4'",  
#                         "simplejson (>2.2); python_version == '2.5'",  
#                        ]