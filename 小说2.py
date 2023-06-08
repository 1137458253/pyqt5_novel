import math
import os
import re
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor
from queue import PriorityQueue
from random import random
import requests
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMessageBox, QTableWidgetItem, QPlainTextEdit, QMainWindow, QPushButton, \
    QWidget
from PyQt5 import QtWidgets, QtCore
import sys
from PyQt5.QtCore import *
import time
from fake_useragent import UserAgent
from lxml import etree


h = {        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
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



def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


# 这里执行单个下载的核心代码
class DownloadThreadCore(QRunnable):
    communication = None

    def __init__(self):
        super(DownloadThreadCore, self).__init__()

    def run(self):
        try:
            url, num, head=self.kwargs["url"],self.kwargs["num"],self.kwargs["head"]
            dirpath = str(self.communication.novel_name) + "/"
            textpath = dirpath + str(head) + ".txt"

            istxtExists = os.path.exists(textpath)

            if istxtExists:
                print(str(head) + ".txt" + "文件已存在")
                return
            else:
                h['User-Agent'] = str(UserAgent().random)
                try:
                    response1 = requests.get(url=url, headers=h).text
                    x = url.split('.')
                    url = x[0] + "." + x[1] + "." + x[2] + "_2." + x[3]
                    response2 = requests.get(url=url, headers=h).text
                except:
                    h['User-Agent'] = str(UserAgent().random)
                    time.sleep(math.floor(random() * 2))
                    response1 = requests.get(url=url, headers=h).text
                    x = url.split('.')
                    url = x[0] + "." + x[1] + "." + x[2] + "_2." + x[3]
                    response2 = requests.get(url=url, headers=h).text
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
            h['User-Agent'] = str(UserAgent().random)
            response = requests.get(url=url, headers=h)
            print(response)
            etree_html = etree.HTML(response.text)
            Chapter_url_list = etree_html.xpath('//*[@id="list-chapterAll"]/dd/a/@href')
            Chapter_url_list = ['http://www.vbiquge.co' + str(i) for i in Chapter_url_list]
            Chapter_head_list = etree_html.xpath('//*[@id="list-chapterAll"]/dd/a/text()')

        print(len(Chapter_url_list), Chapter_url_list)
        print(len(Chapter_head_list), Chapter_head_list)
        Chapter_num_list = list(range(0, len(Chapter_url_list)))
        Chapter_head_list=list(map(validateTitle,Chapter_head_list))

        dirpath = str(self.communication.novel_name) + "/"
        isdirExists = os.path.exists(dirpath)
        if not isdirExists:
            os.makedirs(dirpath)
            print(str(self.communication.novel_name) + "文件夹创建成功")
        for i in range(len(Chapter_url_list)):
            kwargs = {"length":len(Chapter_url_list),"url": Chapter_url_list[i], "num": Chapter_num_list[i],
                      "head": Chapter_head_list[i]}

            task_thread = DownloadThreadCore()
            task_thread.transfer(kwargs=kwargs, communication=self.communication)
            task_thread.setAutoDelete(True)  # 是否自动删除

            self.pool.start(task_thread)

        print("sssss1111")
        self.pool.waitForDone()  # 等待任务执行完毕
        print("sssss2222")
        dirpath = str(self.communication.novel_name) + "/"
        isdirExists = os.path.exists(dirpath)
        if not isdirExists:
            os.makedirs(dirpath)
            print(str(self.communication.novel_name) + "文件夹创建成功")
        try:
            with open(str(self.communication.novel_name) + ".txt", 'a+', encoding='utf-8') as f:
                for Chapter_head in Chapter_head_list:
                    textpath = dirpath + str(Chapter_head) + ".txt"

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

class MyThread(QThread):
    def __init__(self, func, kwargs):
        try:
            super().__init__()
            self.func = func
            self.kwargs = kwargs
        except Exception as e:
            print(e)


    def run(self):
        try:
            self.func(**self.kwargs)
        except Exception as e:
            print(e)

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
            max_thread_number=max_thread_number
        )

    def run(self):
        self.task.start()


class SearchThread(QThread):
    #线程结束返回信息  提示框显示只能这种方式
    sinout=pyqtSignal(str)
    def __init__(self, communication):
        """
        :param communication:通讯
        """
        super(SearchThread, self).__init__()
        #初始化任务
        self.communication=communication #type: Book
    def run(self):
        try:
            self.communication.ui.progressBar.setValue(0)
            info = self.communication.ui.comboBox.currentText()
            print(info)
            print(f"第{self.communication.page}页")
            if (info == "69书屋"):
                pass
            if (info == "笔趣阁"):
                # 根据page加载
                if self.communication.flag == 0:
                    h = {
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                        "Cache-Control": "max-age=0",
                        "Connection": "keep-alive",
                        "Content-Length": "27",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Cookie": "articlevisited=1",
                        "DNT": "1",
                        "Host": "www.vbiquge.co",
                        "Origin": "http://www.vbiquge.co",
                        "Referer": "http://www.vbiquge.co/search/",
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50"
                    }
                    h['User-Agent'] = str(UserAgent().random)
                    text = self.communication.ui.lineEdit.text()
                    index_url = "http://www.vbiquge.co/search/"
                    print(text)
                    data = {
                        'searchkey': text,
                        'submit': ''
                    }
                    response = requests.post(url=index_url, headers=h, data=data).text
                    etree_html = etree.HTML(response)
                    url_list = etree_html.xpath('//*[@class="bookinfo"]/h4/a/@href')
                    url_list = ['http://www.vbiquge.co' + str(i) for i in url_list]
                    head_list = etree_html.xpath('//*[@class="bookinfo"]/h4/a/text()')
                    author_list = etree_html.xpath('//*[@class="bookinfo"]/div[1]/text()')
                    self.communication.url_list = url_list
                    self.communication.head_list = head_list
                    self.communication.author_list = author_list
                    # 分析页数，分页加载
                    self.communication.total = int(math.ceil(len(url_list) / 30))
                    # self.communication.ui.page.setText(f"{self.communication.page}/{self.communication.total}")
                    url_list1 = url_list[30 * (self.communication.page - 1):30 * self.communication.page]
                    head_list1 = head_list[30 * (self.communication.page - 1):30 * self.communication.page]
                    author_list1 = author_list[30 * (self.communication.page - 1):30 * self.communication.page]
                    for i in range(0, len(url_list1)):
                        self.communication.ui.content.setItem(i, 0, QTableWidgetItem(f"{head_list1[i]}"))
                        self.communication.ui.content.setItem(i, 1, QTableWidgetItem(f"{author_list1[i]}"))
                        self.communication.ui.content.setItem(i, 2, QTableWidgetItem(f"{url_list1[i]}"))
                elif self.communication.flag == 1:
                    url_list1 = self.communication.url_list[30 * (self.communication.page - 1):30 * self.communication.page]
                    head_list1 = self.communication.head_list[30 * (self.communication.page - 1):30 * self.communication.page]
                    author_list1 = self.communication.author_list[30 * (self.communication.page - 1):30 * self.communication.page]
                    for i in range(0, len(url_list1)):
                        self.communication.ui.content.setItem(i, 0, QTableWidgetItem(f"{head_list1[i]}"))
                        self.communication.ui.content.setItem(i, 1, QTableWidgetItem(f"{author_list1[i]}"))
                        self.communication.ui.content.setItem(i, 2, QTableWidgetItem(f"{url_list1[i]}"))
                self.communication.ui.page.setText(f"{self.communication.page}/{self.communication.total}")
                self.communication.ui.progressBar.setValue(100)

                self.sinout.emit("搜索完成！")

        except Exception as e:
            print("搜索线程出错",e)
            self.sinout.emit("搜索出错！")

#下载线程
# class DownloadThread(QThread):
#     #传出信息 int 信息类别 str 信息内容
#     '''
#     int:
#       1: 表示传回消息
#       2: 表示线程结束
#
#     '''
#     sinout=pyqtSignal(int,str)
#     #传入下载地址 小说名
#     def __init__(self,url,novel_name):
#         super(DownloadThread, self).__init__()
#         self.url=url
#         self.novel_name=novel_name
#     def run(self):
#         try:
#             h = {
#                 "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#                 "Accept-Encoding": "gzip, deflate",
#                 "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
#                 "Cache-Control": "max-age=0",
#                 "Connection": "keep-alive",
#                 # "Cookie": "articlevisited=1",
#                 "DNT": "1",
#                 "Host": "www.vbiquge.co",
#                 # "If-Modified-Since": "Wed, 21 Apr 2021 00:28:38 GMT",
#                 "Referer": "http://www.vbiquge.co/search/",
#                 "Upgrade-Insecure-Requests": "1",
#                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50"
#             }
#             h['User-Agent'] = str(UserAgent().random)
#             response = requests.get(url=self.url, headers=h)
#             print(response)
#             etree_html = etree.HTML(response.text)
#             Chapter_url_list = etree_html.xpath('//*[@id="list-chapterAll"]/dd/a/@href')
#             Chapter_url_list = ['http://www.vbiquge.co' + str(i) for i in Chapter_url_list]
#             Chapter_head_list = etree_html.xpath('//*[@id="list-chapterAll"]/dd/a/text()')
#             # print(len(Chapter_url_list), Chapter_url_list)
#             # print(len(Chapter_head_list), Chapter_head_list)
#             Chapter_num_list = []
#             for num in range(0, len(Chapter_url_list)):
#                 Chapter_num_list.append(num)
#
#             print(Chapter_url_list)
#             for i in range(0, len(Chapter_url_list)):
#                 try:
#                     thread = MyThread(func=getcontent,
#                                       kwargs={"self": self, "url": Chapter_url_list[i], "num": Chapter_num_list[i],
#                                               "head": Chapter_head_list[i]})
#                     thread.start()
#                 except:
#                     print(f'第{i}章 线程启动失败')
#                 finally:
#                     time.sleep(random())
#             # dirpath = str(self.novel_name) + "/"
#             # file_nums = sum([len(files) for root, dirs, files in os.walk(dirpath)])
#             # if (file_nums > 0):
#             #     print("读取到" + dirpath + "目录下有" + str(file_nums) + "个文件")
#             # print("___________", file_nums, len(Chapter_head_list), "______________")
#             # # 没下好的话重新下载三次
#             # for i in range(0, 3):
#             #     if (file_nums != len(Chapter_head_list)):
#             #         for i in range(0, len(Chapter_url_list)):
#             #             try:
#             #                 thread = MyThread(func=getcontent,
#             #                                   kwargs={"self": self, "url": Chapter_url_list[i],
#             #                                           "num": Chapter_num_list[i],
#             #                                           "head": Chapter_head_list[i]})
#             #                 thread.start()
#             #             except:
#             #                 print(f'第{i}章 线程启动失败')
#             #     else:
#             #         break
#             # print("开始合并")
#             # combine(self, Chapter_head_list)
#             self.sinout.emit(1,"下载完成")
#         except Exception as e:
#             self.sinout.emit(2, f"下载出错！原因：{e}")
#             print("DownloadThread error",e)

#下载所有章节
def getcontent(self,url, num, head):
    try:
        print(url,num,head)
        dirpath=   str(self.novel_name) + "/"
        textpath = dirpath+str(head)+".txt"
        isdirExists = os.path.exists(dirpath)
        istxtExists = os.path.exists(textpath)
        if not isdirExists:
            os.makedirs(dirpath)
            print(str(self.novel_name)+"文件夹创建成功")
        if istxtExists:
            print(str(head)+".txt"+"文件已存在")
            return
        else:
            h = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                # "Cookie": "articlevisited=1",
                "DNT": "1",
                "Host": "www.vbiquge.co",
                # "If-Modified-Since": "Thu, 07 Mar 2019 20:54:17 GMT",
                "Referer": "http://www.vbiquge.co/5_5283/",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50"
            }
            h['User-Agent'] = str(UserAgent().random)
            try:
                response1 = requests.get(url=url, headers=h).text
                x = url.split('.')
                url = x[0] + "." + x[1] + "." + x[2] + "_2." + x[3]
                response2 = requests.get(url=url, headers=h).text
            except:
                h['User-Agent'] = str(UserAgent().random)
                time.sleep(math.floor(random() * 2))
                response1 = requests.get(url=url, headers=h).text
                x = url.split('.')
                url = x[0] + "." + x[1] + "." + x[2] + "_2." + x[3]
                response2 = requests.get(url=url, headers=h).text
            # print(response)
            etree_html1 = etree.HTML(response1)
            title1 = etree_html1.xpath('//*[@ class="pt10"]/text()')[0]
            content1 = etree_html1.xpath('string(//*[@ id="rtext"])')
            etree_html2 = etree.HTML(response2)
            title2 = etree_html2.xpath('//*[@ class="pt10"]/text()')[0]
            content2 = etree_html2.xpath('string(//*[@ id="rtext"])')
            print(num, title1)
            print(num, title2)
            with open(textpath, 'w') as file:  # 创建并打开一个文件
                file.write(title1 + "\n" + content1 + "\n" +title2 + "\n"+content2 )  # 放进去内容，写入
                file.close()  # 关闭
            dirpath = str(self.novel_name) + "/"
            # file_nums = sum([len(files) for root, dirs, files in os.walk(dirpath)])
            # self.ui.progressBar.setValue(round(float(file_nums/len(Chapter_url_list))*100))
    except:
            # print(url, num, head)

            QMessageBox.about(self.ui, "提示", "下载错误，请稍后重试")

#合并章节
def combine(self,Chapter_head_list):
    dirpath = str(self.novel_name) + "/"
    for Chapter_head in Chapter_head_list:
        textpath = dirpath + str(Chapter_head) + ".txt"
        f=open(str(self.novel_name)+".txt", 'a+',encoding='utf-8')
        istxtExists = os.path.exists(textpath)
        if not istxtExists:
            print(str(Chapter_head) + ".txt" + "文件不存在")
            continue
        else:
            file=open(textpath)  # 创建并打开一个文件
            print(Chapter_head)
            f.write(file.read()+'\n')
            file.close()  # 关闭
            f.close()

#获取章节
def getchapter(self,url):
    try:
        h = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
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
        h['User-Agent'] = str(UserAgent().random)
        response = requests.get(url=url, headers=h)
        print(response)
        etree_html = etree.HTML(response.text)
        Chapter_url_list = etree_html.xpath('//*[@id="list-chapterAll"]/dd/a/@href')
        Chapter_url_list = ['http://www.vbiquge.co' + str(i) for i in Chapter_url_list]
        Chapter_head_list = etree_html.xpath('//*[@id="list-chapterAll"]/dd/a/text()')
        # print(len(Chapter_url_list), Chapter_url_list)
        # print(len(Chapter_head_list), Chapter_head_list)
        Chapter_num_list = []
        for num in range(0, len(Chapter_url_list)):
            Chapter_num_list.append(num)

        print(Chapter_url_list)
        for i in range(0, len(Chapter_url_list)):
            try:
                thread = MyThread(func=getcontent,
                                  kwargs={"self": self, "url": Chapter_url_list[i], "num": Chapter_num_list[i],
                                          "head": Chapter_head_list[i]})
                thread.start()
            except:
                print(f'第{i}章 线程启动失败')
            finally:
                time.sleep(random())
        dirpath = str(self.novel_name) + "/"
        file_nums = sum([len(files) for root, dirs, files in os.walk(dirpath)])
        if (file_nums > 0):
            print("读取到" + dirpath + "目录下有" + str(file_nums) + "个文件")
        print("___________", file_nums, len(Chapter_head_list), "______________")
        # 没下好的话重新下载三次
        for i in range(0, 3):
            if (file_nums != len(Chapter_head_list)):
                for i in range(0, len(Chapter_url_list)):
                    try:
                        thread = MyThread(func=getcontent,
                                          kwargs={"self": self, "url": Chapter_url_list[i], "num": Chapter_num_list[i],
                                                  "head": Chapter_head_list[i]})
                        thread.start()
                    except:
                        print(f'第{i}章 线程启动失败')
            else:
                break
        print("开始合并")
        combine(self,Chapter_head_list)
        QMessageBox.about(self.ui, "提示", "下载完成")
    except:
        QMessageBox.about(self.ui, "提示", "下载错误，请稍后重试")


class Book(QWidget):
    page = 1
    novel_name=''
    total = 0
    flag = 0
    # Queue = PriorityQueue()
    # 搜索出的链接
    url_list = []
    # 搜索出的书名
    head_list = []
    # 搜索出的作者
    author_list = []

    #int:code表示不同的信号
    #str 信号字符内容

    #str
    download_sin=pyqtSignal(int,str,int)

    def __init__(self):
        super(Book, self).__init__()
        # 从文件中加载UI定义
        self.ui = uic.loadUi("novel.ui")
        self.ui.button1.clicked.connect(self.search)
        # 搜索
        self.ui.button2.clicked.connect(self.download)
        # 下载
        self.ui.lineEdit.returnPressed.connect(self.search)
        # 搜索回车
        self.ui.comboBox.currentIndexChanged.connect(self.changedir)
        # 监听下拉框
        self.ui.next.clicked.connect(self.nextpage)
        # 页码+1
        self.ui.previous.clicked.connect(self.prepage)
        # 页码-1
        self.ui.refresh.clicked.connect(self.search)
        # 刷新
        self.ui.progressBar.setRange(0,100)
        # 进度条
        self.ui.lineEdit.textChanged.connect(self.changetext)

        #绑定下载召回信号
        self.download_sin.connect(self.download_callback)
        self.downloadThread=None

    def search(self):
        try:
            #开启搜索线程
            self.searchThread=SearchThread(communication=self)
            self.searchThread.start()
            #绑定搜索召回参数
            self.searchThread.sinout.connect(self.search_callback)

        except Exception as e:
            print("search error",e)

    # 重构关闭
    def closeEvent(self, event):
        if self.downloadThread is not None:

            self.downloadThread.task.pool.globalInstance().cancelAll()

        event.accept()
        # 退出所有线程
        os._exit(0)

    def search_callback(self,info):
        self.mes("搜索停止",info)

    def mes(self,title,info):
        QMessageBox.about(self.ui, title, info)

    def download(self):
        try:
            currentrow = self.ui.content.currentRow()
            head = self.ui.content.item(currentrow, 0).text()
            author = self.ui.content.item(currentrow, 1).text()
            url = self.ui.content.item(currentrow, 2).text()
            print("download", currentrow, head, author, url)
            self.novel_name = head
            # thread = MyThread(func=getchapter,kwargs={"self": self, "url": url})
            # thread.start()

            #再开启线程之前设置urls,因为线程是传入self,可在线程中读取要下载的链接
            self.urls=[url]

            #开启下载线程 传入该类和最大线程数
            self.downloadThread=DownloadThread(self,20)
            self.downloadThread.start()

        except Exception as e:
            print(e)
            QMessageBox.about(self.ui, "停止下载", "下载错误，请稍后重试")

    def download_callback(self,code,info,length):
        try:
            if code==2:#表示输出信息
                file_nums = sum([len(files) for root, dirs, files in os.walk(info)])
                self.ui.progressBar.setValue(round(float(file_nums/length)*100))
            elif code==1:
                QMessageBox.about(self.ui, "停止下载", info)
            elif code==3:
                QMessageBox.about(self.ui, "下载完成", info)
                # 恢复按键


        except Exception as e:
            print('download_callback error',e)


    def changedir(self):
        info = self.ui.comboBox.currentText()
        # widget = QPushButton(str(5-1), self)
        # self.ui.addWidget(widget,1,0)
        print("changedir", info)
        # if (info == "69书屋"):
        #     QMessageBox.about(self.ui, "提示", "请自备梯子")

    def changetext(self):
        self.flag=0
        self.page=1

    def nextpage(self):
        if (self.page < self.total):
            self.page += 1
            self.ui.content.clearContents()
            self.flag=1
            self.search()
        else:
            QMessageBox.about(self.ui, "提示", "已经到底了")
        print(self.page)

    def prepage(self):
        if (self.page > 1):
            self.page -= 1
            self.ui.content.clearContents()
            self.flag = 1
            self.search()
        else:
            QMessageBox.about(self.ui, "提示", "不能再往前了")
        print(self.page)




if __name__ == "__main__":
    app = QApplication([])
    book = Book()
    book.ui.show()
    app.exec_()
