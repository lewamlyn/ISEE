# -*- coding:UTF8 -*-
import re
import requests
import json
import datetime
from bs4 import BeautifulSoup

class ZJUAccount:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:84.0) Gecko/20100101 Firefox/84.0',
        }
        self.login_url = 'https://zjuam.zju.edu.cn/cas/login'
        self.pubkey_url = 'https://zjuam.zju.edu.cn/cas/v2/getPubKey'

    def login(self):
        """
        登录函数
        :return: session
        """
        # 获取公钥
        pubkey = self.session.get(self.pubkey_url).json()
        exponent, modulus = pubkey['exponent'], pubkey['modulus']

        data = {
            'username': self.username,
            'password': self._rsa_encrypt(self.password, exponent, modulus),
            'execution': self._get_execution(),
            'authcode': '',
            '_eventId': 'submit'
        }
        resp = self.session.post(self.login_url, data=data)

        # 登录成功，获取姓名
        if self.check_login():
            print(re.search('nick: \'(.*?)\'', resp.text).group(1), '登录成功!')
            return self.session
        else:
            print('登录失败。')
            return
    
    def logincourse(self,url):
        """
        登录函数
        :return: session
        """
        # 获取公钥
        pubkey = self.session.get(self.pubkey_url).json()
        exponent, modulus = pubkey['exponent'], pubkey['modulus']

        data = {
            'username': self.username,
            'password': self._rsa_encrypt(self.password, exponent, modulus),
            'execution': self._get_execution(),
            'authcode': '',
            '_eventId': 'submit'
        }
        resp = self.session.post(url=url, data=data)

        # 登录成功，获取姓名
        if self.check_login():
            print(re.search('nick: \'(.*?)\'', resp.text).group(1), '登录成功!')
            return self.session
        else:
            print('登录失败。')
            return

    def _rsa_encrypt(self, password, exponent, modulus):
        """
        RSA加密函数
        :param password: 原始密码
        :param exponent: 十六进制 exponent
        :param modulus: 十六进制 modulus
        :return: RSA 加密后的密码
        """
        password_bytes = bytes(password, 'ascii')
        password_int = int.from_bytes(password_bytes, 'big')
        e_int = int(exponent, 16)
        m_int = int(modulus, 16)
        result_int = pow(password_int, e_int, m_int)
        return hex(result_int)[2:].rjust(128, '0')

    def _get_execution(self):
        """
        从页面HTML中获取 execution 的值
        :return: execution 的值
        """
        resp = self.session.get(self.login_url)
        return re.search('name="execution" value="(.*?)"', resp.text).group(1)

    def check_login(self):
        """
        检查登录状态，访问登录页面出现跳转则是已登录，
        :return: bool
        """
        resp = self.session.get(self.login_url, allow_redirects=False)
        if resp.status_code == 302:
            return True
        return False

    def get_todo(self):
        sess = self.login()
        resp = sess.get(url='https://courses.zju.edu.cn/api/todos?no-intercept=true')
        info = json.loads(resp.text)
        todolists = []
        for idx in range(len(info['todo_list'])):
            course = info['todo_list'][idx]['course_name'] + ': ' + info['todo_list'][idx]['title'] +'** ' + get_ddl(time = info['todo_list'][idx]['end_time'])
            todolists.append(course)
        
        todolists.sort(key=get_todo_day)
        return todolists

def get_ddl(time):
    ddl = datetime.datetime.strptime(time,'%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.utcnow()
    st = str(ddl)
    t = str(int(st[-15:-13])).zfill(2) + st[-13:-7]
    if int(st[:2]) >= 10:
        s = str(int(st[:2])).zfill(2) + st[2:9] + t
    else:
        s = str(int(st[:2])).zfill(2) + st[1:8] + t
    return s

def get_todo_day(todolist):
    return todolist[-17:-6]

def get_notice(num):
    req = requests.get(url = 'http://www.isee.zju.edu.cn/tzggwxw/list.psp')
    req.encoding = 'utf-8'
    html = req.text
    bf = BeautifulSoup(html, 'html.parser')
    texts = bf.find_all('div', class_='list_content')
    notices = []
    for idx in range(num):
        notice = texts[idx].find('a')
        notices.append(notice.string)
    return notices