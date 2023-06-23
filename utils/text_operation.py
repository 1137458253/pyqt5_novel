import os
import time
from fake_useragent import UserAgent
import requests
import math
import random
from lxml import etree
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread



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
                # file.close()  # 关闭
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