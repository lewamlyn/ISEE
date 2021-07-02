# -*-coding:utf-8 -*-
import requests
import json
import math
import os
import sys

class bili:
    def __init__(self, search_name , search_uid = '928123'):
        self.search_uid = search_uid
        self.search_name = search_name
        self.fanju = ''
        self.upload_message = ''
        self.check_new = False

    def init_fanju(self):
        self.fanju = self.search_name

    def Read_catalog(self):
        catelog = []
        fileName = sys.path[0] + '/' + self.search_name + '.txt'
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
        space_url = 'https://space.bilibili.com/' + self.search_uid
        search_url = 'https://api.bilibili.com/x/space/arc/search'
        mid = space_url.split('/')[-1]
        sess = requests.Session()
        search_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'application/json, text/plain, */*'}

        # 获取视频个数
        ps = 1
        pn = 1
        search_params = {'mid': mid,
                        'ps': ps,
                        'tid': 0,
                        'keyword': self.fanju,
                        'pn': pn}
        req = sess.get(url=search_url, headers=search_headers, params=search_params, verify=False)
        info = json.loads(req.text)
        video_count = info['data']['page']['count']

        ps = 10
        page = math.ceil(video_count/ps)
        videos_list = []
        for pn in range(1, page+1):
            search_params = {'mid': mid,
                            'ps': ps,
                            'tid': 0,
                            'keyword': self.fanju,
                            'pn': pn}
            req = sess.get(url=search_url, headers=search_headers, params=search_params, verify=False)
            info = json.loads(req.text)
            vlist = info['data']['list']['vlist']
            for video in vlist:
                title = video['title']
                # bvid = video['bvid']
                # vurl = 'http://www.bilibili.com/video/' + bvid
                # videos_list.append([title, vurl])
                videos_list.append(title)
        
        #print('共 %d 个视频' % len(videos_list))
        old = self.Read_catalog()
        if old == videos_list :
            self.check_new = False
            self.upload_message = self.search_name + ': ' + old[0] + ' 已更新'
            print(self.search_name + ' 未更新')
        else:
            self.check_new = True
            offset = len(videos_list) - len(old)
            for idx in range (offset):
                self.upload_message = self.search_name + ': ' + videos_list[idx] + ' 已更新'
                print(self.search_name + ': ' + videos_list[idx] + ' 已更新')
        return videos_list

    def Write_catalog(self,catelog_name):
        fileName = sys.path[0] + '/' + self.search_name + '.txt'
        fp = open(fileName,'w+')
        for i in range(len(catelog_name)):
            fp.write(str(catelog_name[i])+'\n')
        fp.close()