# CrawlerTool

### 一些笔记

<b>爬虫三要素: 分析、抓取、(处理)存储（、挖掘、展示）

一、分析

1. 研究目标网站是通过什么来限制爬虫, 一般在header中添加User-Agent(一般没必要换)、Referer、Host等即可, 有必要时上cookies池(注意cookies过期事件)、IP池、或者内置浏览器引擎的爬虫, 某些特殊数据甚至可能需要抓包研究。

2. 尽量减少请求次数, 能抓列表页就不抓详情页。

3. 不要只看 Web 网站, 还有移动版、 App 和 H5, 它们的反爬虫措施一般比较少, 所有社交网站爬虫, 优先选择爬移动版。

4. 如果真的对性能要求很高, 可以考虑多线程、异步甚至分布式, 前提有IP代理池或对方不限制访问频率。


二、抓取

常规

1. url合规化处理、有效判重

2. urllib打开网页, 下载文件。urllib2 has been moved to urllib.request in python3。urllib是基于httplib封装, 偶尔会抛出connection reset by peer异常, 换httplib2貌似就不出现问题了, 这点留待验证。httplib2效率似乎比httplib差。另外发现了一个PyCURL似乎效率更高。

3. requests支持提交GET/POST/PUT/DELETE各种类型的请求(写API方便), 支持重定向, cookies等, 也支持https, 只是https要ssl, 效率只能比http低一些。获取单个页面的话, urllib 和 requests(基于urllib3) 没什么区别。请求复杂的话, 果断是requests开发效率高, 但如果考虑异步I/O, requests缺陷就是直接使用不能异步调用, requests版本是urllib3的封装, urllib3默认是不开启keepalive长连接的, 而且requests爬取大文件比较慢, [Very slow read of large files compared to many other modules/binaries (e.g. urllib/curl/wget) ](https://github.com/kennethreitz/requests/issues/2745), 以及also, [requests has poor performance streaming large binary responses](https://github.com/kennethreitz/requests/issues/2371)。

4. 使用phantomjs或selenium, 模拟浏览器提交类似用户的操作, 处理js动态产生的网页。或者也可以找到对方js文件里的函数用urllib.parse写个post请求。

5. 下载请求用gzip形式下载到本地解压, 降低网络资源负荷。

6. 解析网页BeautifulSoup, 遇到一些结构错误的网页, bs无法正确解析, 只能上re正则, 另外还有lxml可用, 熟悉JQuery的可以用Pyquery。

7. 破解图片验证码, pytesser或pandas或numpy等。


高效

1. IP池：网络上有廉价的代理IP(1元4000个左右), 100个IP中, 平均可用的在40-60左右, 访问延迟均在200以上。也可以可以写一个爬虫, 专门爬代理ip/高匿ip, 然后验证, 能用的全部放到队列里。因为使用IP代理后, 延迟加大, 失败率提高, 所以可以将爬虫框架中将请求设计为异步, 将请求任务加入请求队列(RabbitMQ、redis), 调用成功后再进行回调处理, 失败则重新加入队列, 每次请求都从IP池中取IP, 如果请求失败则从IP池中删除该失效的IP。

2. 维护一个公用队列, 对这个队列进行获取URL和处理。

3. 多线程/多进程, 之前一直觉得Python多线程是鸡肋, 但目前发现还是有点用的, Python多线程虽然不能并行, 但是可以并发, 即使cpu计算下是无用处, 但对于网络io操作还是是有优势的, 像爬虫这种io密集的任务, 绝大多数时间爬虫是在等待socket返回数据, 这个时候C代码里是有release GIL的, 最终结果是某个线程等待IO的时候其他线程可以继续执行, 效率并不低。当然多线程不宜开太多, 太多的线程对于系统来说是个不小的负担, 毕竟上下文切换是有消耗成本, 但还是比开进程消耗的系统资源少, 而且在多进程下需要注意的东西实在不少, 比如数据库连接的cursor游标、数据的共享, 所以视情况采用多线程还是多进程。multiprocessing这个module有一个dummy的sub module, 它是基于multithread实现了multiprocessing的API。使用multiprocessing的Pool, 就是使用多进程实现了concurrency。from multiprocessing import Pool。如果把这个代码改成下面这样, 就变成多线程实现concurrency。from multiprocessing.dummy import Pool。两种方式都跑一下, 哪个速度快用哪个就行了。另外还发现concurrent.futures这个东西, 包含ThreadPoolExecutor和ProcessPoolExecutor, 可能比multiprocessing更简单。如果运行的线程很多, 频繁的切换线程会十分影响工作效率。所以最好还是能通过调试找出任务调度的时间平衡点。

4. 异步, 基于Twisted的Scrapy框架或基于tornado的pyspider, 或使用tornado、asyncio自行在代码中构建异步并发。

5. 分布式抓取调度, 消息队列redis或RabbitMQ, 任务调度schedule。分布式制约爬行速度的首要是带宽, 具体需要多大带宽要看服务器的并发能力来合理设置, 先看下服务器爬行时的情况, cpu满没满载, 带宽峰值多少, 内存占用等情况来购买服务器。


三、存储

1. 编码处理: 略

2. 文件处理: 略

3. 有效存储: 略


四、反爬虫

1. 本质: 在尽量减少对正常用户的干扰的情况下尽可能的加大爬虫的成本。

    爬虫是机器, 不是人：

    特点1：非人, 所以爬虫访问速度快, 访问次数多。

    特点2：非人, 所以人做不到的事情爬虫能做到。
    
    特点3：非人, 所以人能做到的事情爬虫做不到。


2. 针对特点1

    url  递增数字后(部分)随机打乱

    限制有一定行为模式而且频繁访问的ip (避免封整个IP段如学校等)

    验证header属性如User-Agent或者增加动态字段入维护cookie池但爬虫框架一般都支持cookie。

    限制登录访问, 比如, github 用的是 rate limit, 就搜索接口而言, 对非登录用户限制非常严格, 一小时只允许几十次搜索。

    一定时间内总请求达到数量弹出验证码弹窗。

    复杂建模, 特定数据受到非正常量级的请求。



3. 针对特点2

    诱捕, 特定URL进入后封IP


4. 针对特点3

    js监听点击、键盘跳转, 加密动态token甚至对加密库再进行混淆, 或者全站ajax, 以及图灵测试, 杀死非动态解析爬虫


5. 针对其他

    代理IP黑名单。

    拿到阿里云、腾讯云、新浪云等云机房ip段, 来自这些ip段的均复杂验证码伺候。ip段直接问客服, 或者有几台他们不同地域的机房的机器, ip段有规律。

    当然防爬有误报是正常的, 所以一般反爬系统都要做一个容限, 只有超过一定阀值了才会 bang 掉你。即使 bang 掉了, 一般也是让你填一个验证码。无论你是做验证码识别, 还是花钱人肉打码, 他的目的其实都达到了：增加爬取者的成本。

    另一种方式是判断出爬虫后, 不封IP, 而是提供比较真实的假数据, 穿插历史数据和相邻项目的数据, 让他们抓几个月后才发现数据不是全部正确, 白白浪费时间。


### 其他

下载图片时gzip碰到一个bug:

      File "/Users/hipponensis/myprojects/crawlertool/douban_movies.py", line 136, in crawler_image
        image_data = g.read()
      File "/Users/hipponensis/.pyenv/versions/3.5.1/lib/python3.5/gzip.py", line 274, in read
        return self._buffer.read(size)
      File "/Users/hipponensis/.pyenv/versions/3.5.1/lib/python3.5/gzip.py", line 461, in read
        if not self._read_gzip_header():
      File "/Users/hipponensis/.pyenv/versions/3.5.1/lib/python3.5/gzip.py", line 409, in _read_gzip_header
        raise OSError('Not a gzipped file (%r)' % magic)

看了[这个](http://stackoverflow.com/questions/4928560/how-can-i-work-with-gzip-files-which-contain-extra-data), 了解到原因是内置模块设计不合理。

又看了[这个](http://stackoverflow.com/questions/13137817/how-to-download-image-using-requests)和[这个](http://stackoverflow.com/questions/16813267/python-gzip-refuses-to-read-uncompressed-file), 最后使用shutil.copyfileobj问题解决, 但数据未压缩比较耗流量, 等下次抽空优化。