# -*- coding: utf-8 -*-
__author__ = 'hipponensis'

"""爬取代理IP"""


import time
import logging
import operator
import redis
import multiprocessing
import requests
import urllib.parse
import gevent
from bs4 import BeautifulSoup
from gevent import monkey; monkey.patch_all()

SNIFFER = {
    'PROCESS_NUM': 4,
    'THREAD_NUM': 500,
    'PROXY_TYPE': [0, 1, 2, 3],  # 高匿, 普匿, 透明: 3, 2, 1
    'TARGET': 'http://www.baidu.com',
    'TIMEOUT': 10,
    'OUTPUT': True,  # 是否将结果输出到文件（`data/`）
    'BACKEND': '127.0.0.1:6379',  # 是否将结果保存到redis（不保存则为''）    redis-cli    keys ipproxy:*    zcard ipproxy:1  zrange ipproxy:1 0 787
    'KEY_PREFIX': 'ipproxy:',  # redis key前缀
}

LOGGER = {
    "PATH": '/var/log/crawlertool/proxy_ip.log'
}

def get_logger():
    logger = logging.getLogger('ipproxy')
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        # logging format
        fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        # filehandler
        fh = logging.FileHandler(LOGGER['PATH'])
        fh.setFormatter(fmt)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
        # streamhandler
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        ch.setLevel(logging.INFO)
        logger.addHandler(ch)

    return logger


logger = get_logger()



"""
IP struct:
    ip = {
        "ip": "127.0.0.1",
        "port": "8888",
        "info": "XXXXX",
        "type": 1,     # type, 1: 透明, 2: 匿名, 3: 高匿名
    }
"""

class Base(object):
    """ Daily.py Hourly.py 公共基础类 """

    def crawl(self):
        """ 针对不同网站做特化 """
        pass

    def get(self, url, encoding=None, headers=None):
        logger.info('crawl: %s', url)
        try:
            r = requests.get(url, headers=headers) if headers else requests.get(url)
            if encoding:
                r.encoding = encoding

            if r.status_code == requests.codes.ok:
                soup = BeautifulSoup(r.text, "html5lib")
                return self.parse(soup)
            else:
                raise Exception("HTTP Response Code: %s" % r.status_code)

        except Exception as e:
            logger.error('Crawl error: %s', e)

        return []

    def parse(self, soup):
        """ 针对不同网站做特化 """
        pass


"""每日获取"""
class CZ88(Base):
    """ http://www.cz88.net/proxy/http_2.shtml """

    def crawl(self):
        base = "http://www.cz88.net/proxy/"
        proxyip = []
        pages = ["index.shtml"]
        pages.extend(["http_%d.shtml" % i for i in range(2, 11)])
        for page in pages:
            proxyip.extend(self.get(urllib.parse.urljoin(base, page), encoding="GBK"))

        return proxyip

    def parse(self, soup):
        result = []
        soup = soup.find("div", id="boxright").find_all("li")
        keys = ["ip", "port", "type", "info"]
        for s in soup[1:]:
            try:
                ip = {}
                for idx, val in enumerate(s.stripped_strings):
                    ip[keys[idx]] = val

                ip['type'] = 1
                result.append(ip)
            except Exception as e:
                logger.error('CZ88 parse error: %s', e)

        return result


class KuaiDaiLi(Base):
    """ http://blog.kuaidaili.com/ """

    def crawl(self):
        base = "http://blog.kuaidaili.com/"
        proxyip = []
        r = requests.get(base)
        if r.status_code  == requests.codes.ok:
            soup = BeautifulSoup(r.text, "html5lib")
            for s in soup.find_all("article")[:2]:
                proxyip.extend(self.get(s.find("a")["href"]))

        else:
            logger.error("KuaiDaiLi crawl root fail, HTTP Response Code: %s", r.status_code)

        return proxyip

    def parse(self, soup):
        result = []
        s = soup.find("div", class_="entry-content").find_all("p")
        for d in s[1].stripped_strings:
            try:
                rst = d.split(u"\xa0\xa0", 2)
                if len(rst) != 3:
                    continue

                ip = {
                    "ip": rst[0].split(":")[0],
                    "port": rst[0].split(":")[1],
                    "info": rst[2],
                }
                if rst[1] == "透明":
                    ip["type"] = 1
                elif rst[1] == "匿名":
                    ip["type"] = 2
                elif rst[1] == "高匿名":
                    ip["type"] = 3
                else:
                    ip["type"] = 0

                result.append(ip)

            except Exception as e:
                logger.error('KuaiDaiLi parse error: %s', e)

        return result



"""实时获取"""
class KuaiDaiLi2(Base):
    """ www.kuaidaili.com """

    def crawl(self):
        base = "http://www.kuaidaili.com/proxylist/"
        proxyip = []
        for i in range(1, 11):
            proxyip.extend(self.get(urllib.parse.urljoin(base, str(i))))

        return proxyip

    def parse(self, soup):
        result = []
        for s in soup.find("table").find_all("tr")[1:]:
            try:
                d = s.find_all("td")
                ip = {
                    "ip": d[0].string,
                    "port": d[1].string,
                    "info": d[5].string,
                    "type": 0,
                }
                if d[2].string == "透明":
                    ip["type"] = 1
                elif d[2].string == "匿名":
                    ip["type"] = 2
                elif d[2].string == "高匿名":
                    ip["type"] = 3

                result.append(ip)

            except Exception as e:
                logger.error('KuaiDaiLi2 parse error: %s', e)

        return result


class XiCiDaiLi(Base):
    """ www.xicidaili.com """

    def crawl(self):
        base = "http://www.xicidaili.com"
        proxyip = []
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
        }
        for u in ["nn", "nt", "wn", "wt"]:
            proxyip.extend(self.get(urllib.parse.urljoin(base, u), headers=headers))

        return proxyip

    def parse(self, soup):
        result = []
        for s in soup.find("table").find_all("tr")[1:]:
            try:
                d = s.find_all("td")
                ip = {
                    "ip": d[2].string,
                    "port": d[3].string,
                    "info": "",
                    "type": 0,
                }
                info = d[4].find("a")
                if info:
                    ip["info"] = info.string

                if d[5].string == "透明":
                    ip["type"] = 1
                elif d[5].string == "匿名":
                    ip["type"] = 2
                elif d[5].string == "高匿":
                    ip["type"] = 3

                result.append(ip)

            except Exception as e:
                logger.error('XiCiDaiLi parse error: %s', e)

        return result


class IP66(Base):
    """ www.66ip.cn """

    def crawl(self):
        base = "http://www.66ip.cn"
        proxyip = []
        for i in range(1, 11):
            proxyip.extend(self.get(urllib.parse.urljoin(base, "%s.html" % i), encoding='UTF-8'))

        return proxyip

    def parse(self, soup):
        result = []
        for s in soup.find_all("table")[2].find_all("tr")[1:]:
            try:
                d = s.find_all("td")
                ip = {
                    "ip": d[0].string,
                    "port": d[1].string,
                    "info": d[2].string,
                    "type": 0,
                }
                if d[3].string == "透明":
                    ip["type"] = 1
                elif d[3].string == "匿名":
                    ip["type"] = 2
                elif d[3].string == "高匿代理":
                    ip["type"] = 3

                result.append(ip)

            except Exception as e:
                logger.error('IP66 parse error: %s', e)

        return result


class IP66API(Base):
    """ http://www.66ip.cn/nm.html """

    def crawl(self):
        proxyip = []
        for c in range(3):
            # 普通代理IP
            pt = "http://www.66ip.cn/mo.php?tqsl=800"
            proxyip.extend(self.set_type(self.get(pt), 1))
            # 超级匿名
            nm = "http://www.66ip.cn/nmtq.php?getnum=800&anonymoustype=4&proxytype=2&api=66ip"
            proxyip.extend(self.set_type(self.get(nm), 3))
            for i in range(1, 4):
                # 透明，普匿，高匿
                nm = "http://www.66ip.cn/nmtq.php?getnum=800&anonymoustype=%s&proxytype=2&api=66ip" % i
                proxyip.extend(self.set_type(self.get(nm), i))

        return proxyip

    def parse(self, soup):
        result = []
        for d in soup.find('body').contents:
            try:
                d = str(d).strip()
                if d != '' and d[0].isdigit():
                    ip = {
                        "ip": d.split(':')[0],
                        "port": d.split(':')[1],
                        "info": "",
                        "type": 0,
                    }
                    result.append(ip)
            except Exception as e:
                logger.error('IP66API parse error: %s', e)

        return result

    def set_type(self, proxyip=[], iptype=0):
        result = []
        for ip in proxyip:
            ip['type'] = iptype
            result.append(ip)

        return result


class IP002(Base):
    """ http://www.ip002.com/free.html """

    def crawl(self):
        base = "http://www.ip002.com/free.html"
        proxyip = self.get(base, encoding="GBK")
        return proxyip

    def parse(self, soup):
        result = []
        s = soup.find("table").find_all("tr")
        for d in s:
            try:
                w = d.find_all("td")
                ip = {
                    "ip": w[0].string,
                    "port": w[1].string,
                    "info": w[3].string,
                    "type": 0,
                }
                if w[2].string == "透明":
                    ip['type'] = 1
                elif w[2].string == "高匿":
                    ip['type'] = 3

                result.append(ip)

            except Exception as e:
                logger.error('IP002 parse error: %s', e)

        return result


class CNProxy(Base):
    """ http://cn-proxy.com """

    def crawl(self):
        base = "http://cn-proxy.com"
        proxyip = self.get(base)
        return proxyip

    def parse(self, soup):
        result = []
        for s in soup.find_all("table"):
            for t in s.find_all("tr")[2:]:
                try:
                    ip = self._parse(t.find_all("td"))
                    result.append(ip)

                except Exception as e:
                    logger.error('CNProxy parse error: %s', e)

        return result

    def _parse(self, d=[]):
        ip = {
            "ip": d[0].string,
            "port": d[1].string,
            "info": d[2].string,
            "type": 3,
        }
        return ip


class CNProxyForeign(CNProxy):
    """ http://cn-proxy.com/archives/218 """

    def crawl(self):
        base = "http://cn-proxy.com/archives/218"
        proxyip = self.get(base)
        return proxyip

    def _parse(self, d=[]):
        ip = {
            "ip": d[0].string,
            "port": d[1].string,
            "info": d[3].string,
            "type": 0,
        }
        if d[2].string == "透明":
            ip["type"] = 1
        elif d[2].string == "匿名":
            ip["type"] = 2
        elif d[2].string == "高度匿名":
            ip["type"] = 3

        return ip




class Validator(object):
    def __init__(self):
        self.target = SNIFFER['TARGET']
        self.timeout = SNIFFER['TIMEOUT']
        self.process_num = SNIFFER['PROCESS_NUM']
        self.thread_num = SNIFFER['THREAD_NUM']

    def run_in_multiprocess(self, proxy_list):
        """ 多进程 """
        result_queue = multiprocessing.Queue()
        proxy_partitions = self.partite_proxy(proxy_list)
        process = []
        for partition in proxy_partitions:
            p = multiprocessing.Process(target=self.process_with_gevent, args=(result_queue, partition))
            p.start()
            process.append(p)

        for p in process:
            p.join()

        result = {}
        for p in process:
            result.update(result_queue.get())

        return result

    def partite_proxy(self, proxy_list):
        """ 按process_num数对proxy_list进行分块 """
        if len(proxy_list) == 0:
            return []

        result = []
        step = int(len(proxy_list) / self.process_num + 1)
        for i in range(0, len(proxy_list), step):
            result.append(proxy_list[i:i+step])

        return result

    def process_with_gevent(self, result_queue, proxy_list):
        """ 采用gevent进行处理 """
        jobs = [gevent.spawn(self.validate_job, proxy_list) for i in range(self.thread_num)]
        gevent.joinall(jobs)
        result = {}
        for job in jobs:
            result.update(job.value)

        result_queue.put(result)

    def validate_job(self, proxy_list):
        result = {}
        while len(proxy_list) > 0:
            ip_port = proxy_list.pop()
            is_valid, speed = self.validate(ip_port)
            if is_valid:
                result[ip_port] = speed
                logger.info("got an valid ip: %s, time:%s", ip_port, speed)

        return result

    def validate(self, ip_port):
        proxies = {
            "http": "http://%s" % ip_port,
        }
        try:
            start = time.time()
            r = requests.get(self.target, proxies=proxies, timeout=self.timeout)
            if r.status_code == requests.codes.ok:
                speed = time.time() - start
                logger.debug('validating %s, success, time:%ss', ip_port, speed)
                return True, speed

        except Exception as e:
            logger.debug("validating %s, fail: %s", ip_port, e)

        return False, 0


class Sniffer(object):
    """ Validate the proxy ip. """

    def __init__(self):
        self.proxy_type = sorted(SNIFFER['PROXY_TYPE'], reverse=True)
        self.validator = Validator()
        self.redis = None

    def run(self, proxyips):
        result = {}
        proxy_set = self.classify(proxyips)
        for proxy_type in self.proxy_type:
            proxy_list = list(proxy_set.get(proxy_type, set()))
            logger.info('sniffer start, proxy_type: %s, proxy_ip: %s', proxy_type, len(proxy_list))
            result[proxy_type] = self.validator.run_in_multiprocess(proxy_list)
            logger.info('sniffer finish, proxy_type: %s, avail_ip: %s', proxy_type, len(result[proxy_type]))

        if SNIFFER['OUTPUT']:
            try:
                self.save2file(result)
            except Exception as e:
                logger.error("Write file fail, error: %s", e)

        if SNIFFER['BACKEND'] != '':
            try:
                self.redis = redis.StrictRedis(*SNIFFER['BACKEND'].split(':'))
                self.redis.ping()
            except Exception as e:
                logger.error("Backend redis error: %s", e)
                return

            self.reflesh_redis()
            self.save2redis(result)

    def save2file(self, result):
        """ 保存到文件 """
        for proxy_type in result:
            proxy_list = sorted(result[proxy_type].items(), key=operator.itemgetter(1))
            with open('./ip_data/ipproxy-%s.txt' % proxy_type, 'w') as f:
                for ip in proxy_list:
                    f.writelines("%s\t%s\n" % (ip[0], ip[1]))

    def save2redis(self, result):
        """ 保存到redis """
        for proxy_type in self.proxy_type:
            key = '%s%s' % (SNIFFER['KEY_PREFIX'], proxy_type)
            for proxy_ip in result[proxy_type]:
                self.redis.zadd(key, result[proxy_type][proxy_ip], proxy_ip)

    def reflesh_redis(self):
        for proxy_type in self.proxy_type:
            key = '%s%s' % (SNIFFER['KEY_PREFIX'], proxy_type)
            proxy_list = self.redis.zrange(key, 0, -1)
            result = self.validator.run_in_multiprocess(proxy_list)
            # 删除过期数据
            for proxy_ip  in (set(proxy_list) - set(result.keys())):
                self.redis.zrem(key, proxy_ip)

            # 更新数据
            for proxy_ip in result:
                self.redis.zadd(key, result[proxy_ip], proxy_ip)

    def classify(self, proxyip):
        """ 根据匿名程度对ip进行分类 """
        result = {}
        for i in range(4):
            result.setdefault(i, set())

        for ip in proxyip:
            ip_port = "%(ip)s:%(port)s" % ip
            try:
                result[int(ip['type'])].add(ip_port)
            except Exception as e:
                print(e)
                print(ip['ip'], ip['port'], ip['type'])

        return result


class Crawler(object):
    """ Crawl the public proxy ip from the Internet. """
    @classmethod
    def run(cls):
        proxyip = []
        for source in [CNProxy, CNProxyForeign, IP66, IP66API, IP002, XiCiDaiLi, CZ88, KuaiDaiLi, IP002, KuaiDaiLi2]:
            instance = source()
            proxyips = instance.crawl()
            proxyip.extend(proxyips)
            logger.info('%s crawl ip: %s', source, len(proxyips))
        return proxyip


def main():
    proxyips = Crawler().run()
    logger.info('Crawler finish, total ip: %s', len(proxyips))
    sniffer = Sniffer()
    sniffer.run(proxyips)

if __name__ == "__main__":
    main()