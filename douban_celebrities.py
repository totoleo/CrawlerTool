# -*- coding: utf-8 -*-
__author__ = 'hipponensis'

"""姓名, 粉丝数, 基本信息, 链接, 前10/20/40张图片"""

"""性别女, 粉丝数大于100十张, 大于500二十张, 大于1000四十张"""

import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import requests
import shutil
import gzip
import numpy as np
import re
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from openpyxl import Workbook

class DoubanCelebritiesCrawler(object):
    def __init__(self, total):
        self.headers = [
            {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36', 'Accept-Encoding': 'gzip'}
        ]
        self.total = total

    def crawler_images(self):
        for i in range(0, self.total + 1):
            time.sleep(np.random.rand()*5)
            celebrity_url = 'http://movie.douban.com/celebrity/1' + str(i) + '/'
            try:
                req = urllib.request.Request(celebrity_url, headers=self.headers[np.random.randint(0, len(self.headers) - 1)])
                resp = urllib.request.urlopen(req)
                try:
                    g = gzip.GzipFile(mode="rb", fileobj=resp)
                    source_code = g.read()
                except:
                    source_code = resp.read()
                plain_text = str(source_code.decode('utf-8', 'ignore'))
            except (urllib.error.HTTPError, urllib.error.URLError) as e:
                print(e, celebrity_urll)
                plain_text = ''
            soup = BeautifulSoup(plain_text, 'html.parser')
            info = soup.find('div', class_='item').find('div', class_='info')
            sex = info.find('li').get_text()
            if '女' in sex:
                fans = int(soup.find(id='fans').get_text().replace('\n', '').replace(' ', '').split('（')[1].split('）')[0])
                if fans >= 100:
                    if fans >= 1000:
                        limit = 40
                    elif fans >= 500:
                        limit = 20
                    else:
                        limit = 10
                    name = soup.find('div', class_='item').find('a', class_='nbg').get('title')
                    birthday = info.find_next('li').find_next('li').find_next('li').get_text().replace('\n', '').replace(' ', '').split(':')[1]
                    country = info.find_next('li').find_next('li').find_next('li').find_next('li').get_text().replace('\n', '').replace(' ', '').split(':')[1]

                    time.sleep(np.random.rand()*5)
                    all_img_url = 'https://movie.douban.com/celebrity/1' + str(i) + '/photos/'
                    try:
                        req = urllib.request.Request(all_img_url, headers=self.headers[np.random.randint(0, len(self.headers) - 1)])
                        resp = urllib.request.urlopen(req)
                        try:
                            g = gzip.GzipFile(mode="rb", fileobj=resp)
                            source_code = g.read()
                        except:
                            source_code = resp.read()
                        plain_text = str(source_code.decode('utf-8', 'ignore'))
                    except (urllib.error.HTTPError, urllib.error.URLError) as e:
                        print(e, all_img_url)
                        plain_text = ''
                    soup = BeautifulSoup(plain_text, 'html.parser')
                    soup_results = soup.find(id='wrapper').find('ul', class_='poster-col4 clearfix').find_all('img', limit=limit)
                    img_urls = []
                    for link in soup_results:
                        img_urls.append(link.get('src'))

                    k = 1
                    for img_url in img_urls:
                        image_url = img_url.replace('https', 'http').replace('thumb', 'photo')
                        image_name = name + ' ' + birthday + ' ' + country + ' (' + str(k) + ').jpg'
                        k += 1
                        self.crawler_image(image_url, image_name)
                else:
                    pass
            else:
                pass

    def crawler_image(self, image_url, image_name):
        time.sleep(np.random.rand()*5)
        try:
            response = requests.get(image_url, headers=self.headers[np.random.randint(0, len(self.headers) - 1)], stream=True)
            with open('images/celebrities/' + image_name, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(e, image_url)

if __name__ == '__main__':
    DoubanCelebritiesCrawler(355450).crawler_images()

"""http://movie.douban.com/celebrity/1000000/"""
"""http://movie.douban.com/celebrity/1355450/"""