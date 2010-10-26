try:
    import json
except:
    import simplejson as json
    
import validators
import auth
import data

from bottle import request, response, error, run, route, static_file

api_calls = []
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

def api(path='/', auth=None, required=[], optional={}, validate={}, version='0', method='GET'):
    def wrapper(wrapped_function):
        api_calls.append( (method, '%s%s' % (version, path),
            {
            'path':path, 
            'func_name':wrapped_function.func_name,
            'func_doc':wrapped_function.func_doc,
            'func':wrapped_function,
            'required_args':required,
            'optional_args':optional,
            'validators':validate,
            'api_version':version,
            }) )
        def inner(*args, **kwargs):            
            missing = {}
            malformed = {}
            docs = []
            session = None
            
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
                
            if '__args__' in d:
                a = d.popitem('__args__')
            else:
                a = []

            #return wrapped_function(instance, user=None, **d)
            if auth == None:
                return json.dumps(wrapped_function(*a, **d))
            else:
                d['session'] = session
                return json.dumps(wrapped_function(*a, **d))
            
        f = route('/%s/%s' % (version, path.lstrip('/')), method=method)(inner)
        if version == '0':
            route(path, method=method)(inner)
        return f
    return wrapper

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
    @route('/%s/:path#.+#' % url)
    def server_static(path):
        return static_file(path, root=loc)

def nydus_run(host='127.0.0.1', port=8080, reloader=True, config_d={}):
    import bottle
    bottle.debug(True)
    config.update(config_d)
    run(host=host, port=port, reloader=reloader)
