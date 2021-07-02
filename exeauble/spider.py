# -*-coding:utf-8 -*-
import sys
from acfun_spider import * 
from course import *
from bilibili import *

spi = open(sys.path[0] + '/' + 'spider.txt','w+')

# bilibili 视频更新
tian = bili('天天卡牌','10462362')

# bilibili 视频更新
testv = bili('TESTV','11336264')

# bilibili 番剧更新
qidan = bili('奇蛋物语')
qidan.init_fanju()

zuohe = bili('佐贺')
zuohe.init_fanju()

# ACFUN 漫画更新
print('获取ACFUN漫画更新中')
chain = acfun('欺凌者','614361')
list1 = chain.search()
chain.Write_catalog(list1)

child = acfun('推的','614361')
list2 = child.search()
child.Write_catalog(list2)
print('ACFUN漫画更新爬取完毕')

# 贴吧漫画更新
print('获取贴吧更新中')
huiye = tieba_comic('辉夜','https://tieba.baidu.com/home/main?id=tb.1.f8010a90.fAYznIq4thhb46xS7-qepg')
yiquan = tieba_comic('一击','https://tieba.baidu.com/home/main?id=tb.1.f5b2c2d0.HrGbuX37_PlOYh-ZQP3z3w')
print('贴吧漫画更新爬取完毕')

# 学在浙大待办事项
# zju学号、密码初始化
zju = ZJUAccount('','')
todos = zju.get_todo()
try:
    # 信电通知
    notices = get_notice(3)
    print('已获取通知')
    for notice in notices :
        spi.write(notice +'\n') 
except:
    print('请连接浙大校园网')

fp = open(sys.path[0] + '/' + 'todo.txt','w+')
for todo in todos:
    fp.write(str(todo)+'\n')
fp.close()

if huiye :
    spi.write(huiye +'\n')
if yiquan:
    spi.write(yiquan +'\n')
spi.write(chain.upload_message +'\n')
spi.write(child.upload_message +'\n')
spi.close()

# bilibili反爬虫
try:
    # bilibili 视频更新
    bili_list1 = testv.search()
    testv.Write_catalog(bili_list1)

    bili_list2 = tian.search()
    tian.Write_catalog(bili_list2)

    # bilibili 番剧更新
    bili_list3 = qidan.search()
    qidan.Write_catalog(bili_list3)

    bili_list4 = zuohe.search()
    zuohe.Write_catalog(bili_list4)


    spi = open(sys.path[0] + '/' + 'spider.txt','a+')
    spi.write(tian.upload_message +'\n')
    spi.write(testv.upload_message +'\n')
    spi.write(qidan.upload_message +'\n')
    spi.write(zuohe.upload_message +'\n')
    spi.close()
except:
    spi = open(sys.path[0] + '/' + 'spider.txt','a+')
    spi.write(tian.search_name + ': ' + tian.Read_catalog()[0] + '已更新' +'\n')
    spi.write(testv.search_name + ': ' + testv.Read_catalog()[0] + '已更新' +'\n')
    spi.write(qidan.search_name + ': ' + qidan.Read_catalog()[0] + '已更新*' +'\n')
    spi.write(zuohe.search_name + ': ' + zuohe.Read_catalog()[0] + '已更新*' +'\n')
    spi.close()
    print('bilibili 反爬虫生效')