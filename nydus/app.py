from bottle import route, run, response, request
from nydus import api, nydus_run, wrap_object
from nydus import validators
from nydus import auth

@api(path='/')
def index():
    """This method prints hello world. Nothing more."""
    return "hello world"

import sys
if '-test' in sys.argv:
    d = {}
    d['count'] = 0
    
    @api(path='/error/')
    def error():
        raise NydusException( 1000, 'you suck' )

    @api(path='/kwarg/')
    def foo(*args, **kwargs):
        return 'awesometown'

    @api(path='/count/')
    def list():
        """This method will return the current count as an integer."""
        return d['count']
    
    @api(path='/count/incr', optional={"amount":1}, validate={"amount":validators.is_int})
    def incr(amount):
        d['count'] += amount
        return d['count']
    
    @api(path='/count/decr', optional={"amount":1}, validate={"amount":validators.is_int})
    def decr(amount):
        d['count'] -= amount
        return d['count']

    @api(path='/count/double')
    def double():
        d['count'] *= 2
        return d['count']

    @api(path='/count/mod', required=['divisor'], validate={'divisor':validators.is_int})
    def modula(divisor):
        return d['count'] % divisor

    @api(path='/count/', version=1)
    def count1():
        return 'hello world'

    @api(path='/quote', required=['symbol'])
    def quote(symbol):
        import urllib
        return urllib.urlopen('http://download.finance.yahoo.com/d/quotes.csv?s=%s&f=sl1d1t1c1ohgv&e=.csv' % symbol).read().strip().split(',')

    class Test(object):
        def set(self, name):
            self.name = name
            return self.name
        
        def get(self):
            return self.name

    mytest = Test()
    wrap_object(root='/object/', obj=mytest, methods=['set', 'get'])

if __name__ == '__main__':
    auth.use_easy_auth()
    nydus_run(host='127.0.0.1', port=8080)
