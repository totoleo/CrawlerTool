# -*- coding: utf-8 -*-
__author__ = 'hipponensis'


import urllib.request
from bs4 import BeautifulSoup
proxy_support = urllib.request.ProxyHandler({'http':'http://127.0.0.1:1080'})
opener = urllib.request.build_opener(proxy_support)
urllib.request.install_opener(opener)
for i in range(0,5):
    content = urllib.request.urlopen('http://ip.chinaz.com/').read()
    soup=BeautifulSoup(content, "html.parser")
    info=soup.find('div', class_='IcpMain02 bor-t1s02').find('p', class_='getlist pl10').get_text()
    print(info)

