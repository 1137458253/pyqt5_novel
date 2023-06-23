import math
import os
import requests
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QMessageBox, QTableWidgetItem, QWidget, QFileDialog
from fake_useragent import UserAgent
from lxml import etree
from utils.thread_download import DownloadThread


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




# 用来搜索得到书籍
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

                    self.communication.ui.page.setText(f"{self.communication.page}/{self.communication.total}")

                elif self.communication.flag == 1:
                    print("本地取出")
                    url_list1 = self.communication.url_list[
                                30 * (self.communication.page - 1):30 * self.communication.page]
                    head_list1 = self.communication.head_list[
                                 30 * (self.communication.page - 1):30 * self.communication.page]
                    author_list1 = self.communication.author_list[
                                   30 * (self.communication.page - 1):30 * self.communication.page]
                    for i in range(0, len(url_list1)):
                        self.communication.ui.content.setItem(i, 0, QTableWidgetItem(f"{head_list1[i]}"))
                        self.communication.ui.content.setItem(i, 1, QTableWidgetItem(f"{author_list1[i]}"))
                        self.communication.ui.content.setItem(i, 2, QTableWidgetItem(f"{url_list1[i]}"))
                self.communication.ui.page.setText(f"{self.communication.page}/{self.communication.total}")
                # self.communication.ui.progressBar.setValue(100)
                #     self.sinout.emit("搜索完成！")

        except Exception as e:
            print("搜索线程出错",e)
            self.sinout.emit("搜索出错！")





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
        # 默认下载位置为当前工作目录
        self.download_pos = None
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

        self.ui.download_pos.clicked.connect(self.select_pos)

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

    # 选择存放位置
    def select_pos(self):
        # options = QFileDialog.options()
        # options |= QFileDialog.DontUseNativeDialog
        file_name = QFileDialog.getExistingDirectory(self,"select download loacation",)
        self.download_pos = file_name


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
            self.downloadThread = DownloadThread(self, 100)
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
        self.flag = 0
        self.page = 1
        print("内容改变")

    def nextpage(self):
        try:
            if (self.page < self.total):
                self.page += 1
                self.ui.content.clearContents()
                self.flag = 1
                self.search()
            else:
                QMessageBox.about(self.ui, "提示", "已经到底了")
            print(self.page)
        except Exception as e:
            print(e)

    def prepage(self):
        try:
            if (self.page > 1):
                self.page -= 1
                self.ui.content.clearContents()
                self.flag = 1
                self.search()
            else:
                QMessageBox.about(self.ui, "提示", "不能再往前了")
            print(self.page)
        except Exception as e:
            print(e)




if __name__ == "__main__":
    app = QApplication([])
    book = Book()
    book.ui.show()
    app.exec_()
