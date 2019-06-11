# -*- coding:utf-8 -*-
import requests
from faker import Faker
from random import choice
import json
import time
import xlsxwriter
import datetime
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.mime.application import MIMEApplication
import smtplib
import os

class Residence(object):

    # 类属性
    def __init__(self):
        self.url = "http://www.fangdi.com.cn/service/trade/getFirstResidenceStat.action"
        self.sender = 'ayl1991923@qq.com'  # 发件人邮箱账号
        self.my_pass = 'xjgvtqstqkirbcad'  # 发件人授权码
        self.receivers = '807645038@qq.com' # 收件人邮箱账号，我这边发送给自己
        # self.receivers = ['673202141@qq.com', '1271396431@qq.com', '807645038@qq.com', '1135252170@qq.com']
        date_today = datetime.date.today()
        date_l = datetime.timedelta(days=1)
        self.date_y = date_today - date_l
        # table_name是我生成文件时(忽略)的命名，这里解释下
        self.name = '房地网{}新房销售统计'.format(self.date_y) + '.xlsx'

    # 下载器
    def download(self, url):
        fake_ua = Faker()
        agents = [
            fake_ua.chrome(),
            fake_ua.firefox(),
            fake_ua.opera(),
            fake_ua.safari()]
        agent = choice(agents)
        headers = {'User-Agent': agent}
        response = requests.get(url, headers=headers)
        res = response.content.decode('utf-8')
        return res

    # 解析房地网的响应
    def parse_data(self, response):
        rec_data = []
        res_dict = json.loads(response)
        for i in res_dict["FirstResidenceStat"]:
            item = {}
            item['区域'] = i['zonename']
            item['今年已售住宅套数'] = i['z_all_sign_num']
            item['今年已售住宅面积'] = i['z_all_sign_area']
            item['今日已售住宅套数'] = i['z_sign_num']
            item['今日已售住宅面积'] = i['z_sign_area']
            item['今年已售办公套数'] = i['b_all_sign_num']
            item['今年已售办公面积'] = i['b_all_sign_area']
            item['今日已售办公套数'] = i['b_sign_num']
            item['今日已售办公面积'] = i['b_sign_area']
            item['今年已售商业套数'] = i['s_all_sign_num']
            item['今年已售商业面积'] = i['s_all_sign_area']
            item['今日已售商业套数'] = i['s_sign_num']
            item['今日已售商业面积'] = i['s_sign_area']
            item['今年已售其它套数'] = i['q_all_sign_num']
            item['今年已售其它面积'] = i['q_all_sign_area']
            item['今日已售其它套数'] = i['q_sign_num']
            item['今日已售其它面积'] = i['q_sign_area']
            a = time.localtime()
            current_time = time.strftime("%Y-%m-%d %H:%M", a)
            item['时间'] = current_time
            rec_data.append(item)
        return rec_data

    # 生成excel
    def generate_excel(self, rec_data):
        workbook = xlsxwriter.Workbook(self.name)

        worksheet = workbook.add_worksheet()

        # 设定格式，等号左边格式名称自定义，字典中格式为指定选项
        # bold：加粗，num_format:数字格式
        bold_format = workbook.add_format({'bold': True})
        money_format = workbook.add_format({'num_format': '$#,##0'})
        date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})

        # 将二行二列设置宽度为15(从0开始)
        worksheet.set_column(1, 1, 15)

        # 用符号标记位置，例如：A列1行
        worksheet.write('A1', '区域', bold_format)
        worksheet.write('B1', '今日已售住宅套数', bold_format)
        worksheet.write('C1', '今日已售住宅面积', bold_format)
        worksheet.write('D1', '今日已售办公套数', bold_format)
        worksheet.write('E1', '今日已售办公面积', bold_format)
        worksheet.write('F1', '今日已售商业套数', bold_format)
        worksheet.write('G1', '今日已售商业面积', bold_format)
        worksheet.write('H1', '今日已售其它套数', bold_format)
        worksheet.write('I1', '今日已售其它面积', bold_format)

        row = 1
        col = 0
        for item in (rec_data):
            # 使用write_string方法，指定数据格式写入数据
            worksheet.write_string(row, col, item['区域'])
            worksheet.write_string(row, col + 1, str(item['今日已售住宅套数']))
            worksheet.write_string(row, col + 2, str(item['今日已售住宅面积']))
            worksheet.write_string(row, col + 3, str(item['今日已售办公套数']))
            worksheet.write_string(row, col + 4, str(item['今日已售办公面积']))
            worksheet.write_string(row, col + 5, str(item['今日已售商业套数']))
            worksheet.write_string(row, col + 6, str(item['今日已售商业面积']))
            worksheet.write_string(row, col + 7, str(item['今日已售其它套数']))
            worksheet.write_string(row, col + 8, str(item['今日已售其它面积']))
            row += 1
        workbook.close()

    # 发送邮件
    def send_email(self):
        msg = MIMEMultipart()
        msg['From'] = formataddr(["杨力", self.sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['Subject'] = '房地网{}新房成交数据'.format(self.date_y)  # 邮件的主题，也可以说是标题
        filepath = './' + self.name  # 绝对路径
        xlsxpart = MIMEApplication(open(filepath, 'rb').read())
        basename = self.name
        xlsxpart.add_header('Content-Disposition', 'attachment',
                            filename=('gbk', '', basename))  # 注意：此处basename要转换为gbk编码，否则中文会有乱码。
        msg.attach(xlsxpart)
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(self.sender, self.my_pass)  # 括号中对应的是发件人邮箱账号、邮箱授权码
        server.sendmail(self.sender, self.receivers, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        os.remove(filepath)  # 删除文件

    def run(self):
        res = self.download(self.url)
        rec_data = self.parse_data(res)
        self.generate_excel(rec_data)
        self.send_email()


if __name__ == '__main__':
    residence = Residence()
    residence.run()
