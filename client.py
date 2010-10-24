try:
    import json
except:
    import simplejson as json

import httplib
import urllib
import functools
import types

class NydusClient(object):
    def __init__(self, server, version='0'):
        self._host = server
        self._version = version
        self._token = None
        self._server = httplib.HTTP(server)
        self._calls = set()
        self._proxies = set()
        self._reflect()
        
    def __repr__(self):
        return "<NydusClient available_api_calls=%r proxies=%r>" % (list(self._calls), list(self._proxies))

    def _get(self, url, data={}):
        return self._fetch('GET', url, gdata=data)
        
    def _fetch(self, method, url, gdata={}, data={}):
        if self._token:
            if method == 'GET':
                gdata.update({'_auth_token':self._token})
            else:
                data.update({'_auth_token':self._token})
        
        if gdata:
            url = url + "?" + urllib.urlencode(gdata)
            
        self._server.putrequest(method, url)
        self._server.putheader("Host", self._host)
        raw = urllib.urlencode(data)
        self._server.putheader('Content-Length', str(len(raw)))
        
        self._server.endheaders()
        self._server.send(raw)
        reply = self._server.getreply()
        d = self._server.getfile().read()
        try:
            d = json.loads(d)
        except:
            pass
        return reply[0], d
    
    def _handle(self, result):
        if result[0] == 200:
            return result[1]
        else:
            raise Exception( str(result) )
    
    def _reflect(self):
        code, data = self._get('/_api_list/', {'version':self._version})
        if code == 200:
            keys = data.keys()
            keys.sort()
            for key in keys:
                value = data[key]
                p = key.split('/', 1)[1].strip('/')
                if not p:
                    p = '_'

                url = '/%s/%s' % (self._version, value[0].lstrip('/'))
                c = lambda url=url, **kwargs: self._handle(self._get(url, kwargs))
                c.func_doc = str(data[key][2]) + "\nRequired Args: " + str(data[key][4]) + "\nOptional Args:" + str(data[key][5])

                l = p.split('/')
                c.func_name = str(l[-1])
                
                parent = self
                cur = self
                for i in l[:-1]:
                    test = getattr(cur, i, None)
                    if test == None:
                        np = NydusProxy(self)
                        test = np
                        cur._proxies.add(i)
                        setattr(cur, i, np)
                    parent = cur
                    cur = test

                if type(cur) == types.FunctionType:
                    name = cur.func_name
                    np = NydusProxy(self)
                    np._api_call = cur
                    cur = np
                    setattr(parent, name, np)
                    parent._calls.add(name)
                    
                setattr(cur, l[-1], c)
                cur._calls.add(l[-1])

                
class NydusProxy(object):
    def __init__(self, client):
        self.client = client
        self._api_call = None
        self._calls = set()
        self._proxies = set()
        
    def __repr__(self):
        if self._api_call:
            return "<NydusProxy call=%s available_api_calls=%r proxies=%r>" % (str(self._api_call.func_name), list(self._calls), list(self._proxies))
        else:
            return "<NydusProxy available_api_calls=%r proxies=%r>" % (list(self._calls), list(self._proxies))
            
    def _get(*args, **kwargs):
        return self.client._get(*args, **kwargs)
    
    def __call__(self, *args, **kwargs):
        return self._api_call(*args, **kwargs)

if __name__ == '__main__':
    import sys
    if '-gae' in sys.argv:
        x = NydusClient('jitsu.appspot.com')
    else:
        x = NydusClient('localhost:8080')

