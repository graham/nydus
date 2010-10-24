try:
    import json
except:
    import simplejson as json
    
import validators
import auth
import data

from bottle import request, response, error, run, route, static_file

api_calls = {}
config = {'debug':2}

def error400(docs=[], missing={}, malformed={}, func_doc=''):
    response.status = 400
    response.content_type = 'text/plain'

    if config['debug'] == 2 or 'debug_loud' in request.GET:
        d = [ json.dumps([]) ]
        d.append('')
        d.append('/* debug splitter */')
        
        d.append('/* Function Documentation: %s */' % func_doc)
        
        for i in missing:
            d.append('// %r is required for this API call.' % i)
            d.append('')
        if malformed:
            d.append('')
            d.append('// Malformed:')

            for key, string in docs:
                d.append('//   %s: %s' % (key, ', '.join(string)))

    elif 'debug' in request.POST:
        d = [json.dumps( {'missing':missing, 'malformed':malformed, 'docs':docs} )]
    else:
        d = [json.dumps( {'missing':missing, 'malformed':malformed} )]        
    return '\n'.join(d)

def api(path='/', auth=None, required=[], optional={}, validate={}, version=0):
    def wrapper(wrapped_function):
        api_calls['%i%s' % (version, path)] = {
            'path':path, 
            'func_name':wrapped_function.func_name, 
            'func_doc':wrapped_function.func_doc, 
            'func':wrapped_function, 
            'required_args':required, 
            'optional_args':optional, 
            'validators':validate, 
            'api_version':version}
        def inner(*args, **kwargs):            
            missing = {}
            malformed = {}
            docs = []
            
            d = {}
            d.update(optional)
            d.update(request.POST)
            d.update(request.GET)

            if auth:
                try:
                    if '_auth_token' in d:
                        session = auth(d['_auth_token'])
                    elif request.COOKIES.get("_auth_token", None):
                        session = auth(request.COOKIES.get("_auth_token"))
                    else:
                        response.statuscode = 401
                        return json.dumps( {'error':'Authorization Required'} )
                except:
                    response.statuscode = 401
                    return json.dumps( {'error':'Authorization Required'} )
                    
            #validate, required
            #d.update(required)
            
            for i in required:
                if i not in d:
                    missing[i] = ( i, i )
                    
            for key in validate:
                value = validate[key]

                try:
                    d[key] = value(d[key])
                except Exception, e:
                    malformed[key] = value.func_name
                    docs.append( (key, e.args) )
            
            if missing or malformed:
                return error400(docs=docs, missing=missing, malformed=malformed, func_doc=wrapped_function.func_doc)

            if 'session' in d:
                raise Exception("Session is a reserved keyword, don't use it.")

            if '_auth_token' in d:
                d.pop('_auth_token')

            #return wrapped_function(instance, user=None, **d)
            if auth == None:
                return json.dumps(wrapped_function(**d))
            else:
                d['session'] = None
                return json.dumps(wrapped_function(**d))
            
        f = route('/%i/%s' % (version, path.lstrip('/')))(inner)
        if version == 0:
            route(path)(inner)
        return f
    return wrapper

@error(404)
def error404(error): return 'There is no API call at this URL.'

@route('/_api_list/')
def nice_api():
    version = request.GET.get('version', None)
    
    d = {}
    for j in api_calls:
        v = {}
        for i in api_calls[j]['validators']:
            v[i] = (api_calls[j]['validators'][i].func_name, api_calls[j]['validators'][i].func_doc)
        
        if version != None:
            if api_calls[j]['api_version'] == int(version):
                d[j] =  {
                    'path':api_calls[j]['path'],
                    'func_name':api_calls[j]['func_name'],
                    'func_doc':api_calls[j]['func_doc'],
                    'required_args':api_calls[j]['required_args'],
                    'optional_args':api_calls[j]['optional_args'],
                    'validators':v,
                    'api_version':api_calls[j]['api_version']
                }
        else:
            d[j] =  {
                'path':api_calls[j]['path'],
                'func_name':api_calls[j]['func_name'],
                'func_doc':api_calls[j]['func_doc'],
                'required_args':api_calls[j]['required_args'],
                'optional_args':api_calls[j]['optional_args'],
                'validators':v,
                'api_version':api_calls[j]['api_version']
            }
            
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

@route('/_api')
def api_view():
    return get_data_page('index')

@route('/_data/:path')
def server_static_data(path):
    return get_data_page(path)

def route_to_app(p):
    @route('/%s/:path#.+#' % p)
    def server_static(path):
        return static_file(path, root=p)

def nydus_run(config_d={}):
    import bottle
    bottle.debug(True)
    config.update(config_d)
    run(host='localhost', port=8080, reloader=True)
