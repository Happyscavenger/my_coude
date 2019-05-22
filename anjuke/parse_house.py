# coding = utf-8
import requests
from lxml import etree
import re, time
import random
from faker import Faker
from random import choice
import threading
from pymongo import MongoClient
import redis, json, demjson
from copy import deepcopy
from requests.cookies import RequestsCookieJar
import pymysql
from run import AJK_Slide_Captcha

client = MongoClient(
    'mongodb://root:Lansi123@dds-uf605bb40eca92541596-pub.mongodb.rds.aliyuncs.com:3717,dds-uf605bb40eca92542332-pub.mongodb.rds.aliyuncs.com:3717/admin?replicaSet=mgset-4720883')
my_db = client['anjuke']
my_col = my_db['house_col']

pool = redis.ConnectionPool(host='localhost', port=6379)
r = redis.Redis(connection_pool=pool)

def Download_item(url):
    f = Faker()
    agents = [f.chrome(), f.firefox(), f.opera(), f.safari()]
    agent = choice(agents)
    headers = {'User-Agent': agent
               }
    proxies = {'http': 'http://' + proxyip}
    now_time = int(time.time())
    # url = url + "&now_time={}".format(now_time)
    position = re.search("position=(\d+)",url).group(1)
    trading_area_ids = re.search("trading_area_ids=(\d+)",url).group(1)
    url = re.search('(.*?)\?',url).group(1)
    data = {
        'from': 'filter',
        'spread': 'commsearch_p',
        'trading_area_ids':'{}'.format(trading_area_ids),
        'region_ids':'7',
        'position': '{}'.format(position),
        'kwtype': 'filter',
        'now_time': now_time
    }
    # print(url)
    # cookies = requests.cookies.RequestsCookieJar()
    try:
        response = requests.get(url, headers=headers, proxies=proxies,data=data,timeout=30)  # cookies=cookies,
        # cookies.update(response.cookies)
        res = response.content.decode('utf-8')
        if response.status_code == 503:
            res= ''
    except:
        res = ''
    return res

def MyThread(methodThread):
    threads = []
    # n = random.randint(10,20)
    n = 50
    for i in range(n):
        th = threading.Thread(target=methodThread)
        # 加入线程列表
        threads.append(th)
    # 开始线程
    for i in range(n):
        threads[i].setDaemon(True)
        threads[i].start()
    # 结束线程
    for i in range(n):
        threads[i].join()

class ProxyIP:
    ''' 代理IP类 '''

    def __init__(self):
        self.order = '4511ae4cdb951cc33b0ac65b97640a8e'
        self.apiUrl = 'http://api.ip.data5u.com/dynamic/get.html?order=' + self.order
        self.res = ''

    @property
    def GetProxyIp(self):
        ''' 获取代理IP '''
        self.res = requests.get(self.apiUrl).text.strip('\n')
        return self.res

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
            print('更换的IP是{}'.format(proxyip))
            # 标记状态为True
            event.set()

        time.sleep(5)

        if not bol:
            break

def parse_house():
    while True:
        b = r.spop('ftx')
        if b:
            info = json.loads(b.decode('utf-8'))
            url = deepcopy(info)
            while True:
                res = Download_item(url)
                if res:
                    item = {}
                    if 'houseInfo-detail-item' not in res:
                        break
                    else:
                        html = etree.HTML(res)
                        title = html.xpath('//title/text()')[0]
                        if title == '对不起，您要浏览的网页可能被删除，重命名或者暂时不可用':
                            break
                        # phone_num = re.search(r'InquirePhoneNum\((.*?)\);', res, re大花园别墅丨可做4房丨小区安静位置丨全屋地暖丨使用面积大.S).group(1)
                        # phone_num = demjson.decode(phone_num)
                        # broker_id = phone_num['broker_id']
                        # token = phone_num['token']
                        # prop_id = phone_num['prop_id']
                        # prop_city_id = phone_num['prop_city_id']
                        # house_type = phone_num['house_type']
                        # item[
                        #     'phone_url'] = "https://shanghai.anjuke.com/v3/ajax/broker/phone/?broker_id={}&token={}&prop_id={}&prop_city_id={}&house_type={}&captcha=".format(
                        #     broker_id, token, prop_id, prop_city_id, house_type)
                        try:
                            item['url'] = url
                            item['qy'] = html.xpath("//div[@class='houseInfo-content']/p[1]/a[1]/text()")[0]
                            item['jjr'] = html.xpath("//div[@class='brokercard-name']/text()")[0].strip()
                            item['gs'] = html.xpath("//div[@class='broker-company']/p[1]/a/text()")
                            item['gs'] = item['gs'][0].strip() if item['gs'] else ''
                            item['source'] = '安居客'
                            item['xq'] = html.xpath(
                                "//div[@class='houseInfo-content']/a/text()")
                            item['xq'] = item['xq'][0]
                            item['hx'] = html.xpath(
                                "//ul[@class='houseInfo-detail-list clearfix']/li[2]/div[2]/text()")
                            item['hx'] = re.sub(r'[(\r)(\n)(\t)(" ")]', "", item['hx'][0])
                            item['hx'] = item['hx'].strip()
                            item['zj'] = html.xpath('//span[@class="light info-tag"]/em/text()')
                            item['zj'] = int(item['zj'][0]) * 10000 if item['zj'] else 0
                            item['dj'] = html.xpath(
                                "//ul[@class='houseInfo-detail-list clearfix']/li[3]/div[2]/text()")
                            item['dj'] = re.search(r'(\d+)', item['dj'][0]).group(1).replace(' 元/m²', '')
                            adress = html.xpath("//ul[@class='houseInfo-detail-list clearfix']/li[4]/div/p//text()")
                            adress[3] = re.sub(r'[(\r)(\n)(\t)(" ")]', '', adress[3])
                            item['dz'] = adress[0].strip() + adress[1].strip() + adress[2].strip() + adress[3].strip()
                            item['dz'] = re.sub(r"['－']|[' ']", '', item['dz'])
                            item['mj'] = \
                                html.xpath("//ul[@class='houseInfo-detail-list clearfix']/li[5]/div[2]/text()")[0]
                            item['mj'] = item['mj'].replace('平方米', '')
                            # item['down_payment'] = \
                            #     html.xpath("//ul[@class='houseInfo-detail-list clearfix']/li[6]/div[2]/text()")[0].strip()
                            item['nd'] = \
                                html.xpath("//ul[@class='houseInfo-detail-list clearfix']/li[7]/div[2]/text()")[
                                    0].strip()
                            item['nd'] = item['nd'].replace('年', '')
                            # 朝向
                            item['cx'] = \
                                html.xpath("//ul[@class='houseInfo-detail-list clearfix']/li[8]/div[2]/text()")[0]
                            # 房屋类型
                            item['lx'] = \
                                html.xpath("//ul[@class='houseInfo-detail-list clearfix']/li[10]/div[2]/text()")[0]
                            Renovation = \
                                html.xpath("//ul[@class='houseInfo-detail-list clearfix']/li[11]/div[2]/text()")[0]
                            try:
                                item['lc'] = re.findall('.*\(', Renovation)[0].replace('(', '')
                            except:
                                item['lc'] = ''
                            try:
                                item['zg'] = re.findall('共.*层', Renovation)[0].replace('共', '').replace('层', '')
                            except:
                                item['zg'] = ''
                            # 装修
                            item['zx'] = \
                                html.xpath("//ul[@class='houseInfo-detail-list clearfix']/li[12]/div[2]/text()")[0]
                            # 产权年限
                            # item['property_right_years'] = html.xpath(
                            #     "//ul[@class='houseInfo-detail-list clearfix']/li[13]/div[2]/text()")[0]
                            # 电梯
                            # item['elevator'] = \
                            #     html.xpath("//ul[@class='houseInfo-detail-list clearfix']/li[14]/div[2]/text()")[
                            #         0]
                            # 房本年限
                            # item['fbnx'] = html.xpath("//ul[@class='houseInfo-detail-list clearfix']/li[15]/div[2]/text()")[
                            #     0]
                            # 产权性质
                            # item['property_right_nature'] = html.xpath(
                            #     "//ul[@class='houseInfo-detail-list clearfix']/li[16]/div[2]/text()")[0]
                            # 是否一手房源
                            # item['first_hand housing'] = html.xpath(
                            #     "//ul[@class='houseInfo-detail-list clearfix']/li[18]/div[2]/text()")[0]
                            print(item)
                            conn = pymysql.connect(
                                host='rm-uf6t4r3u8vea8u3404o.mysql.rds.aliyuncs.com',
                                port=3306,
                                user='caijisa',
                                passwd='Caijisa123',
                                db='lansi_data_collection',
                                charset='utf8')
                            cursor = conn.cursor()
                            cursor.callproc('CJ_fangtianxia',
                                            (item['qy'], item['dz'], item['xq'], item['zj'], item['dj'], item['mj'],
                                             item['zg'],
                                             item['lc'], item['cx'], item['zx'], item['nd'], item['source'],
                                             item['url'],
                                             '2019-3-25',
                                             item['lx'], item['hx'], item['jjr'], item['gs'], '', ''))
                            conn.commit()
                            cursor.close()
                            conn.close()
                            time.sleep(random.randint(2,5))
                            break
                        except:
                            event.clear()
                            time.sleep(1)
                        event.wait()
                else:
                    event.clear()
                    time.sleep(1)
                event.wait()
        else:
            break


if __name__ == '__main__':
    num = 0
    event = threading.Event()
    event.set()
    bol = True
    pi = ProxyIP()
    proxyip = pi.GetProxyIp  # 代理IP
    th1 = threading.Thread(target=IsSet)
    th1.start()
    MyThread(parse_house)
    # parse_house()
    print('爬取完成')
    bol = False
    # time.sleep(60*60)
