import os
import base64
import urllib

urllib.urlretrieve('http://dl.dropbox.com/s/vodhl20wtk05u9q/js/mootools.js', 'html/mootools.js')
urllib.urlretrieve('http://dl.dropbox.com/s/vodhl20wtk05u9q/jsninja.js', 'html/jsninja.js')

d = {}

for i in os.listdir('html'):
    data = open('html/' + i).read()
    d[i] = base64.encodestring(data)

f = open('data.py', 'w')
for i in d:
    f.write('%s = """\n%s\n"""\n\n' % (i.split('.')[0], d[i]))


f.close()


