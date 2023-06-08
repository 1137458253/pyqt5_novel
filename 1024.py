import json
import re
from random import random
import requests
from fake_useragent import UserAgent
from lxml import etree
def get_content(url):
    h = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close"
    }
    h['User-Agent'] = str(UserAgent().random)
    # proxies = {'http': "127.0.0.1:7890",'https': "127.0.0.1:7890"}
    print(f'https://{url}/thread0806.php?fid=20&search=&page=2')
    reponse=requests.get(f'https://{url}/thread0806.php?fid=20&search=&page=2',headers=h).text
    # print(reponse)
    etree_html = etree.HTML(reponse)
    # head_list = etree_html.xpath('//*[@id="tbody"]/tr/td[2]/h3/a/text()')
    url_list=etree_html.xpath('//*[@id="tbody"]/tr/td[2]/h3/a/@href')
    # print(len(head_list),head_list)
    print(len(url_list),url_list)
    for u in url_list:
        u=f"https://{url}/"+u
        print(u)
        reponse = requests.get(u, headers=h).text
        etree_html = etree.HTML(reponse)
        head = etree_html.xpath('//*[@class="f16"]/text()')
        print(head)
        content = etree_html.xpath('string(//*[@id="conttpc"])')
        print(content)
if __name__=='__main__':
    header={
    "Accept-Encoding": "identity",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "user.xunfss.com",
    "Connection": "close",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
    "Content-Length": "17"
    }
    data={
    'system':'pc',
    'a' : 'get18'
    }
    header['User-Agent'] = str(UserAgent().random)
    response = requests.post('https://user.xunfss.com/app/listapp.php', headers=header,data=data).text
    response=json.loads(response)
    url=response['url1']
    get_content(url)