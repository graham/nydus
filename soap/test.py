from soaplib.service import rpc
from soaplib.service import DefinitionBase
from soaplib.serializers.primitive import String, Integer, Any, SimpleType, AnyAsDict

from soaplib.wsgi import Application
from soaplib.serializers.clazz import Array

'''
This is a simple HelloWorld example to show the basics of writing
a webservice using soaplib, starting a server, and creating a service
client.
'''

class HelloWorldService(DefinitionBase):
    @rpc(AnyAsDict)
    def say_hello(self, name, any, *args, **kwargs):
        print 'hi'

if __name__=='__main__':
    try:
        from wsgiref.simple_server import make_server
        server = make_server('localhost', 7789, Application([HelloWorldService], 'tns'))
        server.serve_forever()
    except ImportError:
        print "Error: example server code requires Python >= 2.5"
