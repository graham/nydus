import uuid
try:
    import json
except:
    import simplejson as json
    
import os
import time

from bottle import response, request
    
class NydusUser(object):
    def __init__(self, uid=None):
        self.uid = uid
        self.password = None
        self.groups = []
        self.data = {}
        if self.uid:
            self.load()
        
    def create(self):
        pass
    
    def load(self):
        pass
    
    def destroy(self):
        pass
    
    def update(self, d):
        pass
    
    def save(self):
        pass
    
    def is_in_group(self, group_name):
        if group_name in self.groups:
            return True
        else:
            return False
    
    @classmethod
    def lookup_by_username(username):
        return None
    
    @classmethod
    def lookup_by_id(uid):
        return None
    

def get_session_key():
    try:
        if request.POST.get('_auth_token', None):
            token = request.POST.get('_auth_token')
            return token
        elif request.GET.get('_auth_token', None):
            token = request.GET.get('_auth_token')
            return token
        elif request.COOKIES.get("_auth_token", None):
            token = request.COOKIES.get("_auth_token")
            return token
        else:
            return None
    except:
        return None

class NydusSession(object):
    def __init__(self, session_key=None):
        self.key = session_key
        self.user = None
        self.user_id = None
        self.last_touched = 0
        self.data = {}
        if self.key:
            self.load()
            
    def create(self):
        pass
    
    def load(self):
        pass
    
    def destroy(self):
        pass
    
    def update(self, d):
        pass
    
    def save(self):
        pass
    
    def exists(self):
        return False

class NydusUserFile(NydusUser):
    def create(self):
        k = '/tmp/users/' + self.uid
        if os.path.exists(k):
            raise NydusException( 100, "User Already Exists" )
        f = open(k, 'w')
        d = {}
        d.update( {'uid':self.uid, 'password':self.password, 'groups':self.groups, 'data':self.data} )
        f.write( json.dumps(d) )
        f.close()
        return self.uid

    def load(self):
        f = open('/tmp/users/' + self.uid)
        data = json.loads(f.read())
        self.__dict__.update(data)
        f.close()

    def destroy(self):
        import os
        os.remove('/tmp/users/' + self.uid)

    def update(self, d):
        self.data.update(d)

    def save(self):
        k = '/tmp/users/' + self.uid
        f = open(k, 'w')
        d = {}
        d.update( {'uid':self.uid, 'password':self.password, 'groups':self.groups, 'data':self.data} )
        f.write( json.dumps(d) )
        f.close()
        return True

    def exists(self):
        if self.uid:
            try:
                return os.path.exists('/tmp/users/' + self.uid)
            except:
                return False
        else:
            return False
            
    @classmethod
    def lookup_by_uid(cls, uid):
        return NydusUserFile(uid)

class NydusSessionFile(NydusSession):
    def create(self):
        import uuid
        if self.key == None:
            self.key = str(uuid.uuid4())
        k = '/tmp/sessions/' + self.key
        f = open(k, 'w')
        d = {}
        d.update( {'key':self.key, 'user_id':self.user_id, 'last_touched':int(time.time()), 'data':self.data} )
        f.write( json.dumps(d) )
        f.close()
        return self.key

    def load(self):
        f = open('/tmp/sessions/' + self.key)
        d = json.loads(f.read())
        self.__dict__.update(d)
        f.close()
        return self

    def destroy(self):
        import os
        os.remove('/tmp/sessions/' + self.key)

    def save(self):
        k = '/tmp/sessions/' + self.key
        f = open(k, 'w')
        d = {}
        d.update( {'key':self.key, 'user_id':self.user_id, 'last_touched':int(time.time()), 'data':self.data} )
        f.write( json.dumps(d) )
        f.close()
        return True

    def exists(self):
        if self.key:
            try:
                return os.path.exists('/tmp/sessions/' + self.key)
            except:
                return False
        else:
            return False
    
    def update(self, d):
        self.data.update(d)

##### easy auth ######
def use_easy_auth():
    from nydus import api

    @api(path='/auth/cookie', explicit_pass_in=True)
    def create_auth_cookie(_api_object):
        """This method will create a session and set its value as a cookie in your browser."""
        x = _api_object.session_class()
        id = x.create()
        response.set_cookie(key='_auth_token', value=id, expires=3600*24, path='/')
        return True

    @api(path='/auth/create', explicit_pass_in=True)
    def create_auth(_api_object):
        """This method will create a session, and write the id back as a JSON string."""
        x = _api_object.session_class()
        id = x.create()
        return id

    @api(path='/auth/is_auth', explicit_pass_in=True)
    def test(_api_object, **kwargs):
        """This method will return a JSON boolean of if the current request is authorized or not."""
        token = get_session_key()
        x = _api_object.session_class()
        x.key = token
        if x.exists():
            return True
        else:
            return False

    @api(path='/auth/is_admin', auth=True)
    def admin_test(session):
        try:
            return 'admin' in session.user.groups
        except:
            return False
        
    @api(path='/auth/check', auth=True)
    def check(session):
        """This method will print 'hello world' if the user is authorized otherwise it will throw a 403 and print an error."""
        return "hello world."

    @api(path='/auth/check_admin', auth=['admin'])
    def admin_check(session):
        """This method will print 'hello world' if the user is authorized and is an admin otherwise it will throw a 403 and print an error."""
        return "Hi admin!"

    @api(path='/auth/logout', explicit_pass_in=True)
    def clear(_api_object):
        """Removes the current _auth_token, returns true if request was previously authorized or false if there was no session."""
        token = get_session_key()
        x = _api_object.session_class(token)
        response.set_cookie(key='_auth_token', value='deleted', expires=-1, path='/')
        #clear_session(session)
        if x.exists():
            x.destroy()
            return True
        else:
            return False
    
    @api(path='/auth/login', required=['uid', 'password'], explicit_pass_in=True)
    def login(_api_object, uid, password, set_cookie=True):
        user = _api_object.user_class.lookup_by_uid(uid)
        if user.password == password:
            x = _api_object.session_class()
            id = x.create()
            x.user_id = uid
            x.save()
            if set_cookie:
                response.set_cookie(key='_auth_token', value=id, expires=3600*24, path='/')
            return id
        else:
            raise NydusException( 0, "Authorization Failed.")
        
    @api(path='/auth/sset', auth=True, explicit_pass_in=True)
    def session_set(_api_object, session, **kwargs):
        x = _api_object.session_class( get_session_key() )
        x.update(kwargs)
        x.save()
        return x.data
        
    @api(path='/auth/sget', auth=True)
    def session_get(session, key=None):
        if key:
            return session.data[key]
        else:
            return session.data
        
    @api(path='/auth/uset', auth=True, explicit_pass_in=True)
    def user_set(_api_object, session, **kwargs):
        user = session.user
        user.update(kwargs)
        user.save()
        return user.data

    @api(path='/auth/uget', auth=True)
    def user_get(session, key=None):
        if key:
            return session.user.data[key]
        else:
            return session.user.data

    @api(path='/auth/admin/create', auth=['admin'], required=['uid', 'password'], explicit_pass_in=True)
    def admin_create_user(_api_object, session, uid, password):
        user = _api_object.user_class()
        user.key = uid
        user.password = password
        user.create()
        user.save()
        return True
    
    @api(path='/auth/admin/destroy', auth=['admin'], required=['uid'], explicit_pass_in=True)
    def admin_user_destroy(_api_object, session, uid):
        user = _api_object.user_class()
        user.key = uid
        user.destroy()
        return True

    @api(path='/auth/admin/add_to_group', auth=['admin'], required=['uid', 'group'], explicit_pass_in=True)
    def admin_user_add_to_group(_api_object, session, uid, group):
        user = _api_object.user_class(uid)
        if group in user.groups:
            return True
        else:
            user.groups.append(group)
            user.save()
            return False
    
    @api(path='/auth/admin/remove_from_group', auth=['admin'], required=['uid', 'group'], explicit_pass_in=True)
    def admin_user_remove_from_group(_api_object, session, uid, group):
        user = _api_object.user_class(uid)
        if group in user.groups:
            user.groups.remove(group)
            user.save()
            return True
        else:
            return False
    
    @api(path='/auth/whoami', auth=True)
    def whoami(session):
        return session.key, session.user.uid
    
    