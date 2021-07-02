# -*-coding:utf-8 -*-
import requests
import os
import re
import math
from bs4 import BeautifulSoup

class acfun:

    def __init__(self, search_name, search_uid):
        self.check_new = False
        self.upload_message = ''
        self.search_name = search_name
        self.search_uid = search_uid

    def Read_catalog(self):
        catelog = []
        fileName = self.search_name + '.txt'
        if os.path.exists(fileName):
            with open(fileName, mode='r') as f:
                for line in f.readlines():
                    line = line.strip('\n')
                    catelog.append(line)
        else:
            with open(fileName, mode='w') as f:
                print('无本地存储信息')
        return catelog

    def search(self):
        search_url = 'https://www.acfun.cn/u/' + self.search_uid
        search_headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
            'accept-language': 'zh-CN,zh;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'referer': search_url,
            'accept': '*/*'}

        # 获取文章总数目
        sess = requests.Session()
        r = sess.get(url=search_url, headers=search_headers)
        html = BeautifulSoup(r.text, 'html.parser')
        tags = html.find('ul',class_='tags')
        counts = tags.find_all('span')
        temp = 0
        for count in counts:
            temp += 1
            if temp == 2:
                article_count = int(count.text)
                break
        
        old_catelog = self.Read_catalog()
        # 获取漫画标题和链接
        pageSize = 100
        pageTotal = math.ceil(article_count/pageSize)
        chapter_names = []
        flag = 0
        for page in range(1, pageTotal+1):    
            search_params = {'page': page,
                            'pageSize': pageSize,
                            "ajaxpipe": 1,
                            'quickViewId': 'ac-space-article-list',
                            'order': 'newest',
                            'type': 'article'}
            r = sess.get(url=search_url, headers=search_headers, params=search_params, verify=False)
            bs = BeautifulSoup(r.text, 'html.parser')
            cartoon_list = bs.find_all('a')

            for cartoon in cartoon_list:      
                name = cartoon.text
                if name.find(self.search_name) > 0 :
                    chapter_names.insert(0, name)
                    if old_catelog:
                        if old_catelog[-1] == name:
                            flag = 1
                            break
        
            # 找到最新一章，中断获取
            if chapter_names:
                if old_catelog:
                    if flag == 1:
                        break
                else:
                    if chapter_names[0].find('#01') > 0:
                        break
        
        if len(chapter_names) == 1:
            chapter_names = old_catelog
            self.check_new = False
            self.upload_message = self.search_name + ': ' + old_catelog[-1] + ' 已更新'
            print(self.search_name + ' 未更新')
        elif len(chapter_names) == 2:
            old_catelog.append(chapter_names[-1])
            chapter_names = old_catelog
            self.check_new = True
            self.upload_message = self.search_name + ': ' + chapter_names[-1] + ' 已更新'
            print(self.search_name + ': ' + chapter_names[-1] + ' 已更新')
        else:
            print()
        
        return chapter_names

    def Write_catalog(self,catelog_name):
        fileName = self.search_name + '.txt'
        fp = open(fileName,'w+')
        for i in range(len(catelog_name)):
            fp.write(str(catelog_name[i])+'\n')
        fp.close()

def tieba_comic(search_name,spider_url):
    catelog = ''
    fileName = search_name + '.txt'
    if os.path.exists(fileName):
        with open(fileName, mode='r+') as f:
            for line in f.readlines():
                line = line.strip('\n')
                catelog = line
    req = requests.get(url = spider_url)
    req.encoding = 'utf-8'
    html = req.text
    bf = BeautifulSoup(html, 'html.parser')
    text = bf.find('div', class_='n_right n_right_first clearfix')
    text = text.find('a', class_='title').string
    if re.findall(search_name,text):
        return text
    else:
        return catelog
