import math
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor
from queue import PriorityQueue
from random import random
import requests
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMessageBox, QTableWidgetItem
from PyQt5 import QtWidgets, QtCore
import sys
from PyQt5.QtCore import *
import time
from fake_useragent import UserAgent
from lxml import etree
class Runthread(QtCore.QThread):
    #  通过类成员对象定义信号对象
    _signal = pyqtSignal(str)

    def __init__(self):
        super(Runthread, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        for i in range(100):
            time.sleep(0.2)
            self._signal.emit(str(i))  # 注意这里与_signal = pyqtSignal(str)中的类型相同
class Example(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        # 按钮初始化
        self.button = QtWidgets.QPushButton('开始', self)
        self.button.setToolTip('这是一个 <b>QPushButton</b> widget')
        self.button.resize(self.button.sizeHint())
        self.button.move(120, 80)
        self.button.clicked.connect(self.start_login)  # 绑定多线程触发事件

        # 进度条设置
        self.pbar = QtWidgets.QProgressBar(self)
        self.pbar.setGeometry(50, 50, 210, 25)
        self.pbar.setValue(0)

        # 窗口初始化
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('OmegaXYZ.com')
        self.show()

        self.thread = None  # 初始化线程

    def start_login(self):
        # 创建线程
        self.thread = Runthread()
        # 连接信号
        self.thread._signal.connect(self.call_backlog)  # 进程连接回传到GUI的事件
        # 开始线程
        self.thread.start()

    def call_backlog(self, msg):
        self.pbar.setValue(int(msg))  # 将线程的参数传入进度条
class book:
    page = 1
    total = 0
    flag = 0
    Queue = PriorityQueue()
    url_list = []
    head_list = []
    author_list = []
    def __init__(self):
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

    def search(self):
        try:
            self.ui.progressBar.setValue(0)
            info = self.ui.comboBox.currentText()
            print(info)
            print(f"第{self.page}页")
            if (info == "69书屋"):
                pass
            if (info == "笔趣阁"):
                # 根据page加载
                if self.flag==0:
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
                    text = self.ui.lineEdit.text()
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
                    self.url_list = url_list
                    self.head_list = head_list
                    self.author_list = author_list
                    # 分析页数，分页加载
                    self.total = int(math.ceil(len(url_list) / 30))
                    # self.ui.page.setText(f"{self.page}/{self.total}")
                    url_list1=url_list[30*(self.page-1):30*self.page]
                    head_list1=head_list[30*(self.page-1):30*self.page]
                    author_list1=author_list[30*(self.page-1):30*self.page]
                    for i in range(0, len(url_list1)):
                        self.ui.content.setItem(i, 0, QTableWidgetItem(f"{head_list1[i]}"))
                        self.ui.content.setItem(i, 1, QTableWidgetItem(f"{author_list1[i]}"))
                        self.ui.content.setItem(i, 2, QTableWidgetItem(f"{url_list1[i]}"))
                elif self.flag==1:
                    url_list1=self.url_list[30*(self.page-1):30*self.page]
                    head_list1=self.head_list[30*(self.page-1):30*self.page]
                    author_list1=self.author_list[30*(self.page-1):30*self.page]
                    for i in range(0, len(url_list1)):
                        self.ui.content.setItem(i, 0, QTableWidgetItem(f"{head_list1[i]}"))
                        self.ui.content.setItem(i, 1, QTableWidgetItem(f"{author_list1[i]}"))
                        self.ui.content.setItem(i, 2, QTableWidgetItem(f"{url_list1[i]}"))
                self.ui.page.setText(f"{self.page}/{self.total}")
                self.ui.progressBar.setValue(100)
        except:
            QMessageBox.about(self.ui, "提示", "加载错误")
        print("search")

    def download(self):
        def getcontent(url, num):
            QApplication.processEvents()
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
            self.Queue.put([num, title1 + "\n" + content1 + "\n" + title2 + "\n" + content2])
            print(self.Queue.qsize())
        try:
            currentrow = self.ui.content.currentRow()
            head = self.ui.content.item(currentrow, 0).text()
            author = self.ui.content.item(currentrow, 1).text()
            url = self.ui.content.item(currentrow, 2).text()
            print("download", currentrow, head, author, url)
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
            url_list = etree_html.xpath('//*[@id="list-chapterAll"]/dd/a/@href')
            url_list = ['http://www.vbiquge.co' + str(i) for i in url_list]
            head_list = etree_html.xpath('//*[@id="list-chapterAll"]/dd/a/text()')
            print(len(url_list), url_list)
            print(len(head_list), head_list)
            num_list = []
            for num in range(0, len(url_list)):
                num_list.append(num)
            # random.shuffle(list_of_idx)
            # with ThreadPoolExecutor(8) as Pool:  # 使用线程池
            for i in range(0, len(url_list)):
                try:
                    thread = threading.Thread(target=getcontent, kwargs={"url": url_list[i],"num":num_list[i]})
                    thread.start()
                except:
                    print(f'第{i}章 线程启动失败')
                finally:
                    time.sleep(math.floor(random()*5))
                # Pool.map(getcontent, url_list,num_list)
            print("_____________",self.Queue.qsize(),len(url_list),"_____________")
            if(self.Queue.qsize()>=len(url_list)):
                with open(f'{head}.txt', 'a+', encoding='utf-8') as f:
                    while not self.Queue.empty():
                        f.write(self.Queue.get()[1])
                    f.close()
            else:
                time.sleep(math.floor(random() * 5))
            if(self.Queue.empty()):
                QMessageBox.about(self.ui, "提示", "下载完成")
        except:
            QMessageBox.about(self.ui, "提示", "下载错误，请稍后重试")

    def changedir(self):
        info = self.ui.comboBox.currentText()
        print("changedir", info)
        if (info == "69书屋"):
            QMessageBox.about(self.ui, "提示", "请自备梯子")
        pass

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
    book = book()
    book.ui.show()
    app.exec_()
