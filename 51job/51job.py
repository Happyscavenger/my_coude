import requests, random
from lxml import etree
import time, re
from queue import Queue
import threading
from copy import deepcopy
import pymysql


class Qianchenwuyou(object):

    def __init__(self):
        self.area_queue = Queue()
        self.plate_queue = Queue()
        self.detail_url_queue = Queue()

    def Download(self, targetUrl):
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
            'User-Agent': ua
        }

        response = requests.get(targetUrl, headers=headers, timeout=30)
        if response.status_code == 200:
            try:
                res = response.content.decode('gbk')
            except:
                res = re.sub(r'<meta http-equiv="Content-Type" content="text/html; charset=gb2312">', '', response.text)
                # fname = 'errors.txt'
                # with open(fname, 'a+') as f:
                #     f.write(response.url + '\n')
        else:
            res = ''
        return res

    def parse_area(self):
        area_dict = {'黄浦区': '020100', '徐汇区': '020300', '长宁区': '020400', '静安区': '020500', '普陀区': '020600',
                     '虹口区': '020800',
                     '杨浦区': '020900', '浦东新区': '021000', '闵行区': '021100', '宝山区': '021200', '嘉定区': '021300',
                     '金山区': '021400', '松江区': '021500', '青浦区': '021600', '奉贤区': '021800', '崇明区': '021900'}
        # area_dict = {'金山区': '021400'}
        for i in area_dict.items():
            url = "https://search.51job.com/jobsearch/ajax/get_districtdibiao.php?rand=0.5991220493668392&jsoncallback=jQuery183010351052960949403_1555999712472&jobarea=020000&district={}".format(
                i[1])
            area_info = []
            area_info.append(i[0])
            area_info.append(url)
            print(area_info)
            self.area_queue.put(deepcopy(area_info))
            print(self.area_queue.qsize())

    def parse_area_url(self):
        while self.area_queue.qsize():
            area_info = self.area_queue.get()
            url = area_info[1]
            res = self.Download(url)
            if res:
                html = etree.HTML(res)
                a_list = html.xpath("//p/a")
                print(len(a_list))
                if len(a_list) != 1:
                    for a in a_list[1:]:
                        item = {}
                        plate_url = a.xpath("./@href")[0]
                        plate_url = re.search(r'\\"(.*)?\\"', plate_url).group(1)
                        item['plate_url'] = plate_url
                        item['area'] = area_info[0]
                        plate_name = a.xpath("./text()")[0]
                        item['plate_name'] = plate_name
                        self.plate_queue.put(deepcopy(item))
                        print(item)
                else:
                    item = {}
                    plate_url = html.xpath("//p/a/@href")[0]
                    plate_url = re.search(r'\\"(.*)?\\"', plate_url).group(1)
                    item['area'] = area_info[0]
                    item['plate_url'] = plate_url
                    plate_name = area_info[0]
                    item['plate_name'] = plate_name
                    self.plate_queue.put(deepcopy(item))
                    print(item)
                time.sleep(random.randint(1,2))

    def get_url(self):
        item = self.plate_queue.get()
        info = {}
        info['area'] = item['area']
        info['plate_name'] = item['plate_name']
        plate_url = item['plate_url']
        # while True:
        res = self.Download(plate_url)
        if res:
            html = etree.HTML(res)
            div_list = html.xpath("//div[@class='dw_table']/div[@class='el']/p")
            for div in div_list[1:]:
                info['url'] = div.xpath('./span/a/@href')[0]
                if "https://jobs.51job.com/" in info['url']:
                    self.detail_url_queue.put(deepcopy(info))
                else:
                    continue
                print(info)
            next_url = html.xpath("//a[text()='下一页']/@href")
            if next_url:
                print(next_url)
                item['plate_url'] = next_url[0]
                self.plate_queue.put(deepcopy(item))
            time.sleep(random.randint(1,2))

    def parse_detail(self):
        info = self.detail_url_queue.get()
        url = info['url']
        # while True:
        res = self.Download(url)
        if res:
            if "很抱歉，你选择的职位目前已经暂停招聘" in res:
                return
            html = etree.HTML(res)
            info['job_id'] = int(re.search(r"/(\d+).html", url).group(1))
            try:
                info['position'] = html.xpath('//div[@class="cn"]/h1/@title')[0]
            except:
                print("出错的url是%s" % url)
            try:
                salary = html.xpath('//div[@class="cn"]/strong/text()')[0]
                if salary:
                    if '千/月' in salary:
                        if "-" in salary:
                            info['min_salary'] = int(float(re.search(r'(.*)?-', salary).group(1)) * 1000)
                            info['max_salary'] = int(float(re.search(r"-(.*)?千/月", salary).group(1)) * 1000)
                        else:
                            info['min_salary'] = int(float(re.search(r"(.*)?千/月", salary).group(1)) * 1000)
                            info['max_salary'] = info['min_salary']
                    elif '万/月' in salary:
                        if "-" in salary:
                            info['min_salary'] = int(float(re.search(r'(.*)?-', salary).group(1)) * 10000)
                            info['max_salary'] = int(float(re.search(r"-(.*)?万/月", salary).group(1)) * 10000)
                        else:
                            info['min_salary'] = int(float(re.search(r"(.*)?万/月", salary).group(1)) * 10000)
                            info['max_salary'] = info['min_salary']

                    elif "万/年" in salary:
                        if "-" in salary:
                            info['min_salary'] = int(float(re.search(r'(.*)?-', salary).group(1)) * 10000) // 12
                            info['max_salary'] = int(float(re.search(r"-(.*)?万/年", salary).group(1)) * 10000) // 12
                        else:
                            info['min_salary'] = int(float(re.search(r"(.*)?万/年", salary).group(1)) * 10000) // 12
                            info['max_salary'] = info['min_salary']
                    # 可能是实习
                    elif "千以下/月" in salary:
                        info['min_salary'] = int(float(re.search(r'(.*)?千', salary).group(1))) * 1000
                        info['max_salary'] = info['min_salary']
                    #以下两类是兼职
                    elif "元/天" in salary:
                        return
                    elif "小时" in salary:
                        return
                    else:
                        print("url is %s"% url)
                        info['min_salary'] = 0
                        info['max_salary'] = 0
                else:
                    info['min_salary'] = 0
                    info['max_salary'] = 0
                    # fname = 'salary_error.txt'
                    # with open(fname, 'a+') as f:
                    #     f.write(url + '\n')
            except:
                info['min_salary'] = 0
                info['max_salary'] = 0
                # fname = 'salary_error.txt'
                # with open(fname, 'a+') as f:
                #     f.write(url + '\n')
            try:
                info['company_addr'] = re.search(r"上班地址：</span>(.*)?</p>", res).group(1).strip()
            except:
                info['company_addr'] = ''
            # 行业
            info['industry'] = html.xpath("//span[@class='i_trade']/following-sibling::a[1]/text()")
            if info['industry']:
                info['industry'] = info['industry'][0]
            else:
                info['industry'] = ""
            info['scale'] = re.search(r'<span class="i_people"></span>(.*)?</p>', res).group(1)
            info['company_type'] = re.search(r'<span class="i_flag"></span>(.*)?</p>', res).group(1)
            conn = pymysql.connect(
                host='xxxxx',
                port=3306,
                user='xxx',
                passwd='xxx',
                db='xxxx',
                charset='utf8')
            cursor = conn.cursor()
            sql = """Replace into `51job` (`ID`,`area`,`plate`,`company_addr`,`position`,`min_salary`,`max_salary`,`industry`,`scale`,`company_type`,`url`)values(%d,"%s","%s","%s","%s",%d,%d,"%s","%s","%s","%s")"""\
                  %(info['job_id'], info['area'], info['plate_name'], info['company_addr'], info['position'],
                info['min_salary'], info['max_salary'], info['industry'], info['scale'], info['company_type'],
                str(info['url']))
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
            time.sleep(random.randint(1,3))

    def MyThread(self, myqueue, methodThread):
        ''' 多线程（队列，方法）'''
        num = 0
        while myqueue.qsize() > 0:
            threads = []
            num += 1
            print(num)
            ts = 50  # 线程数
            if myqueue.qsize() < ts:
                ts = myqueue.qsize()

            for i in range(ts):
                th = threading.Thread(target=methodThread)
                # 加入线程列表
                threads.append(th)
            print('----------------------')
            # 开始线程
            for i in range(ts):
                threads[i].start()

            # 结束线程
            for i in range(ts):
                threads[i].join()
            print('----------------------')
            time.sleep(1)

    def run(self):
        self.parse_area()
        self.parse_area_url()
        self.MyThread(self.plate_queue, self.get_url)
        self.MyThread(self.detail_url_queue, self.parse_detail)
        self.bol = False
        print('采集完成')


if __name__ == '__main__':
    qcwy = Qianchenwuyou()
    qcwy.run()
