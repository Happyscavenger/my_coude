# -*- coding: utf-8 -*-
import scrapy
import re
import time
from copy import deepcopy
from gold_time.items import GoldTimeItem

class JinshiSpider(scrapy.Spider):
    name = 'jinshi'
    allowed_domains = ['jin10.com',"view.jin10.com"]
    time_format = '%Y-%m-%d %X'
    now_time = time.strftime(time_format,time.localtime())
    start_urls = ['https://view.jin10.com/flash?max_time={}'.format(now_time)]

    def parse(self,response):
        data = response.body.decode()
        data = re.findall(r'.*?\((.*?)\);', data, re.S)[0]
        mess = re.findall(r'\{"data":\[(.*?)\],.*\}', data, re.S)[0]
        time_show = re.findall(r'"time_show":"(.*?)",?', mess, re.S)[-1:][0]
        for a in range(60):
            item = GoldTimeItem()
            mess_a = re.findall(r'\{(.*?)\}', mess)[a]
            if mess_a is not None:
                item['id'] = re.findall(r'"id":"(\w+)",?', mess_a, re.S)[0]
                item['title_content'] = re.findall(r'"title_content":"(.*?)",?', mess_a, re.S)
                item['title_content'] = re.sub(r'\\', '', str(item['title_content']))
                item['title_content'] = re.sub(r'<b>|</b>|</b>|<br />|<br />|\r|\n|\t|\s|<br/>|</b>|</br >', '', str(item['title_content']))
                item['time_show'] = re.findall(r'"time_show":"(.*?)",?', mess_a, re.S)[0]
                item['url'] = re.findall(r'"url":"(.*?)",?', mess_a, re.S)[0]
                item['url'] = re.sub(r'(\\)', '', str(item['url']))
            print(item)

            next_url = 'https://view.jin10.com/flash?max_time={}'.format(time_show)
            if next_url is not None:
                yield scrapy.Request(
                    next_url,
                    callback=self.parse,
                    meta={"item": deepcopy(item)}
                )