# -*- coding: utf-8 -*-
__author__ = 'hipponensis'

"""年度: 电影名, 评分, 评价人数, 分类, 电影信息(包括导演演员国家的等), 链接, 封面, 前10张图片"""

"""其他思路: 从电影评论用户(已看1000以上)角度爬, 或从豆列爬直接拿评分人数"""

import sys
import time
import urllib
import requests
import numpy as np
from multiprocessing.dummy import Pool as ThreadPool
from bs4 import BeautifulSoup
from openpyxl import Workbook


# 图片
# def get_image(url,image_path):
#     print("get_image:",url)
#     try:
#         g = gzip.GzipFile(mode="rb",fileobj=urllib.request.urlopen(url))
#         image_data=g.read()
#     except:
#         image_data=urllib.request.urlopen(url).read()
#     filename = url[url.rindex('/') + 1:]
#     #print(filename)
#     img_f = open(image_path + filename, "wb")
#     img_f.write(image_data)
#     img_f.close()