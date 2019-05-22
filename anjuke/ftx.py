# -*- coding: utf-8 -*-
import requests, re, queue, threading, pymysql, time, sys
from bs4 import BeautifulSoup
from pymongo import MongoClient
import random

client = MongoClient(
    'mongodb://root:Lansi123@dds-uf605bb40eca92541596-pub.mongodb.rds.aliyuncs.com:3717,dds-uf605bb40eca92542332-pub.mongodb.rds.aliyuncs.com:3717/admin?replicaSet=mgset-4720883')
db = client.caiji
ftx = db.fangtianxia

c_time = str(time.strftime("%Y-%m-%d"))


# 去除多余的空格和回车
def replaceN(str):
    str = str.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
    return str


class ProxyIP:
    ''' 代理IP类 '''

    def __init__(self):
        self.order = 'cdb53a844238171418b4a9b3436013b5'

        self.apiUrl = 'http://api.ip.data5u.com/dynamic/get.html?order=' + self.order

    # self.res = ''

    @property
    def GetProxyIp(self):
        ''' 获取代理IP '''
        res = requests.get(self.apiUrl).text.strip('\n')
        # if "too many requests" not in res:
        return res


def Download(url):
    ''' 页面下载 '''
    first_num = random.randint(55, 62)
    third_num = random.randint(0, 3200)
    fourth_num = random.randint(0, 140)
    os_type = [
        '(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)', '(X11; Linux x86_64)',
        '(Macintosh; Intel Mac OS X 10_12_6)'
    ]
    chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)

    ua = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
                   '(KHTML, like Gecko)', chrome_version, 'Safari/537.36']
                  )
    headers = {
        'User-Agent': ua,
        'Connection': 'close',
    }
    proxies = {'https': 'https://' + proxyip}
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        # response.encoding = 'GBK'
        soup = BeautifulSoup(response.text, 'lxml')
    except:
        info = sys.exc_info()
        if not 'timed out' in str(info[1]):
            print(threading.currentThread().getName(), info[1])
        return ''
    return soup


def IsSet():
    ''' 线程运行状态 '''
    global num
    while True:
        global proxyip
        # 线程阻塞，更换IP
        if not event.isSet():
            try:
                proxyip = pi.GetProxyIp
            except:
                time.sleep(3)
                print('proxyip出错！！！')
                continue
            num += 1
            print('IP更换次数', num)
            # 标记状态为True
            event.set()
        time.sleep(3)

        if not bol:
            break


def Get():
    for i in ftx.find({"tag": ''}).sort('url', 1):
        myqueue3.put(i['url'])


# 采集案例信息
def Dispose():
    while myqueue3.qsize() > 0:
        htmlUrl = myqueue3.get()
        # print(htmlUrl)
        n = 0
        # soup = Download('http://esf.sh.fang.com' + htmlUrl)
        while True:
            soup = Download('http://esf.sh.fang.com' + htmlUrl)
            if soup == '' or not 'pageConfig.district =' in soup:
                if '未找到相关页面' in soup:
                    print('http://esf.sh.fang.com' + htmlUrl)
                    ftx.remove({'url': htmlUrl})
                    break
                event.clear()
                break
            else:
                break
            event.wait()
        if soup == '' or not 'pageConfig.district =' in soup.text:
            continue
        info = {}
        if 'pageConfig.district =' in soup.text:
            info['来源'] = '房天下'
            try:
                info['区域'] = re.findall('pageConfig.district =\".*\"', soup.text)[0].replace('pageConfig.district =\"',
                                                                                             '').replace(
                    '\"', '')
            except:
                try:
                    info['区域'] = re.findall('pageConfig.district =\'.*\'', soup.text)[0].replace(
                        'pageConfig.district =\'',
                        '').replace(
                        '\'', '')
                except:
                    print('http://esf.sh.fang.com' + htmlUrl)
                    print('错误', soup)

            info['地址'] = re.findall('pageConfig.address=\'.*\'', soup.text)[0].replace('pageConfig.address=\'',
                                                                                       '').replace(
                '\'', '')
            try:
                info['小区'] = re.findall('pageConfig.projname = [\'\"].*[\'\"]', soup.text)[0].replace(
                    'pageConfig.projname = \"', '').replace('\"', '')
            except:
                print('http://esf.sh.fang.com' + htmlUrl)
                print('错误', soup)
            info['年代'] = re.findall('pageConfig.createtime=\'.*\'', soup.text)[0].replace('pageConfig.createtime=\'',
                                                                                          '').replace(
                '\'', '')
            info['朝向'] = re.findall('pageConfig.forward=\'.*\'', soup.text)[0].replace('pageConfig.forward=\'',
                                                                                       '').replace(
                '\'', '')
            info['面积'] = re.findall('pageConfig.area=\'.*\'', soup.text)[0].replace('pageConfig.area=\'', '').replace(
                '\'', '')
            info['楼层'] = re.findall('pageConfig.floor=\'.*\'', soup.text)[0].replace('pageConfig.floor=\'', '').replace(
                '\'', '')
            info['总高'] = re.findall('pageConfig.totalfloor=\'.*\'', soup.text)[0].replace('pageConfig.totalfloor=\'',
                                                                                          '').replace(
                '\'', '')
            try:
                info['总价'] = int(
                    float(
                        re.findall('pageConfig.price=\'.*\'', soup.text)[0].replace('pageConfig.price=\'', '').replace(
                            '\'', '')) * 10000)
            except:
                info['总价'] = 0
            info['单价'] = re.findall('unitprice:\'.*\'', soup.text)[0].replace('unitprice:\'', '').replace(
                '\'', '')
            info['姓名'] = re.findall('pageConfig.agentname=\'.*\'', soup.text)[0].replace('pageConfig.agentname=\'',
                                                                                         '').replace(
                '\'', '')
            try:
                info['电话'] = soup.find('span', {'id': 'phone'}).text
            except:
                info['电话'] = None

            list = soup.findAll('div', {'class': 'trl-item1'})
            info['户型'] = replaceN(list[0].find('div').text)
            info['装修'] = replaceN(list[5].find('div').text)
            info['类别'] = ''
            for i in soup.findAll('div', {'class': 'text-item clearfix'}):
                if i.text.find('建筑类别') >= 0:
                    info['类别'] = i.find('span', {'class': 'rcont'}).text
                    break
                else:
                    continue

            info['中介'] = re.findall('pageConfig.comname=\'.*\'', soup.text)[0].replace('pageConfig.comname=\'',
                                                                                       '').replace(
                '\'', '')
            info['类型'] = re.findall('pageConfig.purpose=\'.*\'', soup.text)[0].replace('pageConfig.purpose=\'',
                                                                                       '').replace(
                '\'', '')
            info['URL'] = 'http://esf.sh.fang.com' + htmlUrl

            print(info)
            conn = pymysql.connect(
                host='rm-uf6t4r3u8vea8u3404o.mysql.rds.aliyuncs.com',
                port=3306,
                user='caijisa',
                passwd='Caijisa123',
                db='lansi_data_collection',
                charset='utf8')
            cursor = conn.cursor()
            cursor.callproc('CJ_fangtianxia',
                            (info['区域'], info['地址'], info['小区'], info['总价'], info['单价'], info['面积'], info['总高'],
                             info['楼层'], info['朝向'], info['装修'], info['年代'], info['来源'], info['URL'], c_time,
                             info['类型'], info['户型'], info['姓名'], info['中介'], info['电话'], info['类别']))
            conn.commit()
            cursor.close()
            conn.close()
            ftx.update({'url': htmlUrl}, {'$set': {
                'tag': '1'
            }})
            time_list = [0.5, 1, 1.5, 2, 2.5, 0.75, 1.25, 1.75, 2.25, 2.5, 2.75, 3]
            time.sleep(random.choice(time_list))


# 多线程（队列，方法）
def MyThread(myqueue, methodThread):
    tag = 0
    while myqueue.qsize() > 0:
        # time.sleep(0.5)
        tag += 1
        print(tag)
        if methodThread == "":
            break

        num = 30
        if myqueue.qsize() < 30:
            num = myqueue.qsize()

        threads = []
        for i in range(num):
            th = threading.Thread(target=methodThread)
            # 加入线程列表
            threads.append(th)

        # 开始线程
        for i in range(num):
            threads[i].start()

        # 结束线程
        for i in range(num):
            threads[i].join()


if __name__ == '__main__':
    while True:
        # 代理IP
        myqueue3 = queue.Queue()
        num = 0  # ip 更换计数
        event = threading.Event()
        event.set()
        bol = True  # 控制线程退出
        pi = ProxyIP()
        proxyip = pi.GetProxyIp
        # 更换IP线程
        th1 = threading.Thread(target=IsSet)
        th1.start()
        Get()
        MyThread(myqueue3, Dispose)
        bol = False  # 退出线程
