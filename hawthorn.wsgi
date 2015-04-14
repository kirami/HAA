'''
def application(environ, start_response):
    status = '200 OK'
    output = 'Hello World!'

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]
'''

import os
import sys


sys.path = ['/home/kirami/webapps/dev/hawthorn', '/home/kirami/webapps/dev/lib/python3.4'] + sys.path

os.environ['PYTHON_EGG_CACHE'] = '/home/kirami/webapps/dev/hawthorn/.python-egg'

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
