try:
    import json
except:
    import simplejson as json
    
import os
from bottle import response, request

def get_session(fss):
    try:
        if request.POST.get('_auth_token', None):
            token = request.POST.get('_auth_token')
            return fss(token)
        elif request.GET.get('_auth_token', None):
            token = request.GET.get('_auth_token')
            return fss(token)
        elif request.COOKIES.get("_auth_token", None):
            token = request.COOKIES.get("_auth_token")
            return fss(token)
        else:
            return None
    except:
        return None

def fs_session_update(session, d):
    session.update(d)
    fs_session_write(session['key'], session)
    return session

def fs_session_write(key, d={}, path_to_sessions='/tmp/sessions'):
    k = path_to_sessions + '/' + key
    f = open(k, 'w')
    d.update( {'key':key} )
    f.write( json.dumps(d) )
    return True

def fs_session(key, path_to_sessions='/tmp/sessions'):
    k = path_to_sessions + '/' + key
    if not os.path.exists(k):
        raise Exception("Authorization Required")
    else:
        data = open(k).read().strip()
        d = json.loads( data )
        d.update( {'key':key} )
        return d
        
def app_engine_session_write(key, d={}):
    pass

def app_engine_session(key):
    pass

##### easy auth ######
def use_easy_auth(fss=fs_session, fsw=fs_session_write):
    from nydus import api
    import uuid

    @api(path='/auth/cookie')
    def create_auth_cookie():
        """This method will create a session and set its value as a cookie in your browser."""
        id = str(uuid.uuid4())
        fsw(id)
        response.set_cookie(key='_auth_token', value=id, expires=3600*24, path='/')
        return True

    @api(path='/auth/create')
    def create_auth():
        """This method will create a session, and write the id back as a JSON string."""
        id = str(uuid.uuid4())
        fsw(id)
        return id

    @api(path='/auth/test')
    def test(**kwargs):
        """This method will return a JSON boolean of if the current request is authorized or not."""

        session = get_session(fss)
        if session != None:
            return True
        else:
            return False
        
    @api(path='/auth/check', auth=fss)
    def check(session):
        """This method will print 'hello world' if the user is authorized otherwise it will throw a 403 and print an error."""
        return "hello world."

    @api(path='/auth/logout')
    def clear():
        """Removes the current _auth_token, returns true if request was previously authorized or false if there was no session."""
        session = get_session(fss)
        response.set_cookie(key='_auth_token', value='deleted', expires=-1, path='/')
        #clear_session(session)
        if session != None:
            return True
        else:
            return False
    
    @api(path='/auth/login', required=['username', 'passwd'])
    def login(username, passwd='foo'):
        id = str(uuid.uuid4())
        fsw(id, {'username':username})
        return id
        
    @api(path='/auth/login_cookie', required=['username', 'passwd'])
    def login_cookie(username, passwd):
        id = str(uuid.uuid4())
        fsw(id, {'username':username})
        response.set_cookie(key='_auth_token', value=id, expires=3600*24, path='/')
        
    @api(path='/auth/set', auth=fss)
    def session_set(session, **kwargs):
        new_session = fs_session_update(session, kwargs)
        return new_session
        
    @api(path='/auth/get', auth=fss)
    def session_get(session, key=None):
        if key:
            return session[key]
        else:
            return session
            