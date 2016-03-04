# CrawlerTool

### 使用
版本: Python3

需要安装的模块: beautifulsoup4, numpy, Workbook

另外使用了urllib: urllib2 has been moved to urllib.request in python3

为什么没用requests:

[Very slow read of large files compared to many other modules/binaries (e.g. urllib/curl/wget) ](https://github.com/kennethreitz/requests/issues/2745)
    
    Very slow read of large files compared to many other modules/binaries (e.g. urllib/curl/wget) 

    Using python 3.4 and requests 2.7.0 (on both Ubuntu 14.04 and Mac OS X), I've noticed that fetching raw content of large files is significantly slower (~5x) with requests than many other applications and python modules, performance as below is typical:

    import requests                                                             
    import urllib.request                                                       
    import time                                                                 

    # returns a 100Mb JSON file                                                                     
    url = 'http://some.host.on.local.network/'

    def with_urllib():                                                          
        with urllib.request.urlopen(url) as f:                                  
            return f.read()                                                     

    def with_requests():                                                        
        return requests.get(url).content                                        

    s = time.time()                                                             
    a = with_urllib()                                                           
    print('urllib:', time.time() - s, 'seconds')                                

    s = time.time()                                                             
    b = with_requests()                                                         
    print('requests:', time.time() - s, 'seconds')                              

    assert a == b
    This outputs:
    urllib: 1.113746166229248 seconds
    requests: 5.458410978317261 seconds

    curl, wget, pycurl and urllib all complete in similar times (~1.1s on average), requests consistently takes ~5.4s on average, even with various combinations of parameters I've tried (e.g. with streaming, with different streaming chunksizes, etc.).

also, [requests has poor performance streaming large binary responses](https://github.com/kennethreitz/requests/issues/2371).

获取单个页面的话，py3 urllib 和 requests(基于urllib3) 没什么区别，主要在于如何快速获取大量网页，如果考虑异步I/O, requests缺陷就是直接使用不能异步调用, 所以暂用urllib, 预计下次更新会尝试 tornado或aiohttp/asyncio 异步.

另外requests支持https很好用, 只是https要ssl，效率只能比http低一些, 目前暂时未用到; requests也支持GET/POST/PUT/DELETE, 比urllib全面, 某些场合下比urllib有用, 比如RESTful API; 当然, 论开发效率, 请求复杂的话，果断是requests开发效率高.

最后一点, urllib是基于httplib封装, 偶尔会抛出connection reset by peer异常, 换httplib2貌似就不出现问题了, 这点留待验证, httplib2效率似乎比httplib差?