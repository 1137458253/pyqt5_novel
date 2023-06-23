from PyQt5.QtCore import QRunnable,QObject,QThreadPool,QThread
from fake_useragent import UserAgent
import os
import requests
import time
import math
import random
from lxml import etree
import re


def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title

# def is_exists(path):
#     if os.path.exists(path):
#         print("")




h = {       "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            # "Cookie": "articlevisited=1",
            "DNT": "1",
            "Host": "www.vbiquge.co",
            # "If-Modified-Since": "Wed, 21 Apr 2021 00:28:38 GMT",
            "Referer": "http://www.vbiquge.co/search/",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50"
        }


# 这里执行单个下载的核心代码
class DownloadThreadCore(QRunnable):
    communication = None

    def __init__(self):
        super(DownloadThreadCore, self).__init__()
        self.h = h

    def run(self):
        try:
            url, num, head=self.kwargs["url"],self.kwargs["num"],self.kwargs["head"]
            if self.communication.download_pos:
                dirpath = os.path.join(self.communication.download_pos,str(self.communication.novel_name))
            else:
                dirpath = str(self.communication.novel_name)

            textpath = os.path.join(dirpath,str(head) + ".txt")

            istxtExists = os.path.exists(textpath)

            if istxtExists:
                print(str(head) + ".txt" + "文件已存在")
                return
            else:
                # 随机生成用户请求头，伪装爬虫
                self.h['User-Agent'] = str(UserAgent().random)
                # 获取文本内容
                try:
                    response1 = requests.get(url=url, headers=self.h).text
                    x = url.split('.')
                    url = x[0] + "." + x[1] + "." + x[2] + "_2." + x[3]
                    response2 = requests.get(url=url, headers=self.h).text

                except:
                    self.h['User-Agent'] = str(UserAgent().random)
                    time.sleep(math.floor(random() * 2))
                    response1 = requests.get(url=url, headers=self.h).text
                    x = url.split('.')
                    url = x[0] + "." + x[1] + "." + x[2] + "_2." + x[3]
                    response2 = requests.get(url=url, headers=self.h).text

                # 解析爬取到的内容

                etree_html1 = etree.HTML(response1)
                title1 = etree_html1.xpath('//*[@ class="pt10"]/text()')[0]
                content1 = etree_html1.xpath('string(//*[@ id="rtext"])')

                etree_html2 = etree.HTML(response2)
                title2 = etree_html2.xpath('//*[@ class="pt10"]/text()')[0]
                content2 = etree_html2.xpath('string(//*[@ id="rtext"])')

                print(num, title1)
                print(num, title2)

                with open(textpath, 'w',encoding="utf-8") as file:  # 创建并打开一个文件
                    file.write(title1 + "\n" + content1 + "\n" + title2 + "\n" + content2)  # 放进去内容，写入
                    file.close()  # 关闭

                dirpath = str(self.communication.novel_name) + "/"
                self.communication.download_sin.emit(2,dirpath,self.kwargs["length"])

        except Exception as e:
            print("DownloadThreadCore error",e)

    # 自定义函数，用来初始化一些变量
    def transfer(self, kwargs, communication):
        """
        :param thread_logo:线程标识，方便识别。
        :param communication:信号
        :return:
        """
        self.kwargs = kwargs
        self.communication = communication #type: Book



# 定义任务，在这里主要创建线程
class Tasks(QObject):
    communication = None
    max_thread_number = 0

    def __init__(self, communication, max_thread_number):
        """
        :param communication:通讯
        :param max_thread_number:最大线程数
        """
        super(Tasks, self).__init__()

        self.h = h
        self.max_thread_number = max_thread_number
        self.communication = communication #type: Book
        #初始化线程池
        self.pool = QThreadPool()
        self.pool.globalInstance()


    def start(self):
        # 设置最大线程数
        self.pool.setMaxThreadCount(self.max_thread_number)
        #下载链接
        Chapter_url_list=[]
        #下载名字
        Chapter_head_list=[]

        #根据主类对象在开启下载线程之前设置的urls做处理
        for url in self.communication.urls:
            self.h['User-Agent'] = str(UserAgent().random)
            response = requests.get(url=url, headers=self.h)
            print(response)
            etree_html = etree.HTML(response.text)
            Chapter_url_list = etree_html.xpath('//*[@id="list-chapterAll"]/dd/a/@href')
            Chapter_url_list = ['http://www.vbiquge.co' + str(i) for i in Chapter_url_list]
            Chapter_head_list = etree_html.xpath('//*[@id="list-chapterAll"]/dd/a/text()')

        print(len(Chapter_url_list), Chapter_url_list)
        print(len(Chapter_head_list), Chapter_head_list)

        Chapter_num_list = list(range(0, len(Chapter_url_list)))
        Chapter_head_list=list(map(validateTitle,Chapter_head_list))

        if self.communication.download_pos:
            dirpath = os.path.join(self.communication.download_pos,str(self.communication.novel_name))
        else:
            dirpath = str(self.communication.novel_name)

        isdirExists = os.path.exists(dirpath)

        if not isdirExists:
            os.makedirs(dirpath)
            print(str(self.communication.novel_name) + "文件夹创建成功")

        # 使用线程池下载当前章节
        for i in range(len(Chapter_url_list)):
            kwargs = {"length":len(Chapter_url_list),"url": Chapter_url_list[i], "num": Chapter_num_list[i],
                      "head": Chapter_head_list[i]}

            task_thread = DownloadThreadCore()
            task_thread.transfer(kwargs=kwargs, communication=self.communication)
            task_thread.setAutoDelete(True)  # 是否自动删除

            self.pool.start(task_thread)

        print("Success initial the thread pool!")
        self.pool.waitForDone()  # 等待任务执行完毕
        print("Thread pool success download the text.")

        if self.communication.download_pos:
            dirpath = os.path.join(self.communication.download_pos, str(self.communication.novel_name))
        else:
            dirpath = str(self.communication.novel_name)

        isdirExists = os.path.exists(dirpath)

        if not isdirExists:
            os.makedirs(dirpath)
            print(str(self.communication.novel_name) + "文件夹创建成功")

        try:
            with open(str(self.communication.novel_name) + ".txt", 'a+', encoding='utf-8') as f:
                for Chapter_head in Chapter_head_list:
                    textpath = os.path.join(dirpath,str(Chapter_head) + ".txt")

                    istxtExists = os.path.exists(textpath)
                    if not istxtExists:
                        print(str(Chapter_head) + ".txt" + "文件不存在")
                        continue
                    else:
                        print(textpath)
                        file = open(textpath,"r",encoding="utf-8")
                        print(Chapter_head)
                        f.write(file.read() + '\n')
                        file.close()  # 关闭
        except Exception as e:
            print(e)

        self.communication.download_sin.emit(3,'下载完毕',0)

# 重写QThread类
class DownloadThread(QThread):
    def __init__(self, communication, max_thread_number):
        """
        :param communication:通讯
        :param max_thread_number:最大线程数
        """
        super(DownloadThread, self).__init__()
        #初始化任务
        self.task = Tasks(
            communication=communication,
            max_thread_number=max_thread_number,
        )

    def run(self):
        self.task.start()

