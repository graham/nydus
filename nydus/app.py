from bottle import route, run, response, request
from nydus import api, nydus_run
from nydus import validators
from nydus import auth

@api(path='/')
def index():
    """This method prints hello world. Nothing more."""
    return "hello world"

d = {}
d['count'] = 0

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


if __name__ == '__main__':
    auth.use_easy_auth()
    nydus_run({})
