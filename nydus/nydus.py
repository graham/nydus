try:
    import json
except:
    import simplejson as json

import config
import validators
import auth
import data

from bottle import request, response, error, run, route, static_file

api_calls = []
config.api_calls = api_calls
default_api = config.NydusAPI()
api = default_api.api
page = default_api.page
    
@error(404)
def error404(error): return 'There is no API call at this URL.'

@route('/_api_list/')
def nice_api():
    version = request.GET.get('version', None)
    
    d = []
    for j in api_calls:
        method, path, data = j

        v = {}
        for i in data['validators']:
            v[i] = (data['validators'][i].func_name, data['validators'][i].func_doc)
        
        if version != None:
            if data['api_version'] == version:
                d.append( (method, path, {
                    'path':data['path'],
                    'func_name':data['func_name'],
                    'func_doc':data['func_doc'],
                    'required_args':data['required_args'],
                    'optional_args':data['optional_args'],
                    'validators':v,
                    'api_version':data['api_version'],
                    'method':method
                }) )
        else:
            d.append( (method, path, {
                'path':data['path'],
                'func_name':data['func_name'],
                'func_doc':data['func_doc'],
                'required_args':data['required_args'],
                'optional_args':data['optional_args'],
                'validators':v,
                'api_version':data['api_version'],
                'method':method
            }) )
            
    return json.dumps(d)
    
import base64
import sys
import os

if '-dev' in sys.argv:
    def get_data_page(name):
        for i in os.listdir('html'):
            check = i.split('.')[0]
            if check == name:
                return open('html/' + i).read()
        return ''
else:
    def get_data_page(name):
        return base64.decodestring(getattr(data, name))

@route('/favicon.ico')
def favicon():
    return get_data_page('favicon')
    
@route('/_api')
def api_view():
    return get_data_page('index')

@route('/_data/:path')
def server_static_data(path):
    return get_data_page(path)
    
def wrap_object(root, obj, methods, **topkwargs):
    for i in methods:
        @api(path='%s%s' % (root, i), **topkwargs)
        def test(__method=i, **kwargs):
            return getattr(obj, __method)(**kwargs)

def route_to_app(url, loc):
    @route('/%s/' % url)
    @route('/%s/:path#.+#' % url)
    def server_static(path='/'):
        if path.endswith('/'):
            path += 'index.html'
        return static_file(path, root=loc)

def nydus_run(host='127.0.0.1', port=8080, reloader=True, config_d={}):
    import bottle
    bottle.debug(True)
    run(host=host, port=port, reloader=reloader)
