from urllib.request import urlopen
import re


URL = 'https://zh.wikipedia.org/wiki/%E5%AE%9D%E5%8F%AF%E6%A2%A6%E5%88%97%E8%A1%A8'
c = urlopen(URL).read().decode('utf-8')
p = re.compile('<td.*?><a.*?>(.*?)</a>')
ns = p.findall(c)
f = open('pkmid.py', 'w')
f.write('pkmid = {\n')
for i, n in enumerate(ns[:151]):
    f.write('    %d: "%s",\n' % (i+1, n))
f.write('}\n')
