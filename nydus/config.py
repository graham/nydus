try:
    import json
except:
    import simplejson as json

import httplib
import urllib
import functools
import types

from bottle import request, response, error, run, route, static_file

config = {'debug':2}

from auth import NydusSessionFile, NydusUserFile

class NydusAPI(object):
    def __init__(self):
        self.live_version = '0'
        self.user_class = NydusUserFile
        self.session_class = NydusSessionFile

    def error400(self, docs=[], missing={}, malformed={}, func_doc=''):
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

    def api(self, path='/', auth=None, required=[], optional={}, validate={}, version=None, method='GET', errors={}, returns=None, explicit_pass_in=False):
        if version == None:
            version = self.live_version
            
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
                'errors':errors,
                'returns':returns
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
                            session = self.session_class(d['_auth_token'])
                        elif request.COOKIES.get("_auth_token", None):
                            session = self.session_class(request.COOKIES.get("_auth_token"))
                        else:
                            response.statuscode = 401
                            return json.dumps( {'error': (401, 'Authorization Required')} )
                    except:
                        response.statuscode = 401
                        return json.dumps( {'error':(401, 'Authorization Required')} )
                        
                    if 'uid' in session.data:
                        session.user = self.user_class(session.data['uid'])

                if session and session.user and auth not in (True, False):
                    # auth == group_name
                    # session should be something
                    found = False
                    for i in auth:
                        if session.user.is_in_group(i):
                            found = 1
                        
                    if not found:
                        response.statuscode = 403
                        return json.dumps( {'error': (403, 'You are not allowed to use this API call.')} )
                    
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
                    return self.error400(docs=docs, missing=missing, malformed=malformed, func_doc=wrapped_function.func_doc)

                if 'session' in d:
                    return json.dumps({'error':(-1,'Session is a reserved word, contact the administrator.')})

                if '_auth_token' in d:
                    d.pop('_auth_token')

                if '__args__' in d:
                    a = d.popitem('__args__')
                else:
                    a = []
                
                if explicit_pass_in:
                    d['_api_object'] = self

                #return wrapped_function(instance, user=None, **d)
                try:
                    if auth == None:
                        return json.dumps(wrapped_function(*a, **d))
                    else:
                        d['session'] = session
                        return json.dumps(wrapped_function(*a, **d))
                except Exception, e:
                    return json.dumps({'error':e.args})

            f = route('/%s/%s' % (version, path.lstrip('/')), method=method)(inner)
            if version == self.live_version:
                route(path, method=method)(inner)
            return f
        return wrapper
