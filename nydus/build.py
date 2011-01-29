import os
import base64
import urllib

urllib.urlretrieve('http://dl.dropbox.com/s/rvm1kmkpnqjpx2b/js/mootools.js', 'html/mootools.js')
urllib.urlretrieve('http://dl.dropbox.com/s/rvm1kmkpnqjpx2b/genie.js', 'html/genie.js')
urllib.urlretrieve('http://dl.dropbox.com/s/rvm1kmkpnqjpx2b/editor.js', 'html/editor.js')

d = {}

for i in os.listdir('html'):
    if i.endswith('~') or i.endswith('pyc'):
        continue
    data = open('html/' + i).read()
    d[i] = base64.encodestring(data)

f = open('data.py', 'w')
for i in d:
    f.write('%s = """\n%s\n"""\n\n' % (i.split('.')[0], d[i]))
f.close()


