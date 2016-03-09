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
        self.headers = [{'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:5.0) Gecko/20100101 Firefox/5.0', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:16.0) Gecko/20121026 Firefox/16.0', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-CN; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101', 'Accept-Encoding': 'gzip'},
            {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1', 'Accept-Encoding': 'gzip'}
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