# import requests
# from faker import Faker
# from random import choice
# import time
#
# url = "https://www.anjuke.com/captcha-verify/?callback=shield"
# # url = "https://shanghai.anjuke.com/sale/?from=navigation"
#
# def Download(url):
#     f = Faker()
#     agents = [f.chrome(), f.firefox(), f.opera(), f.safari()]
#     agent = choice(agents)
#     headers = {'User-Agent': agent}
#     # proxies = {'http': 'http://' + proxyip}
#     now_time = int(time.time())
#     url = url + "&now_time={}".format(now_time)
#     # cookies = requests.cookies.RequestsCookieJar()
#     try:
#         response = requests.get(url, headers=headers, timeout=30)  # cookies=cookies, proxies=proxies,
#         print(response.request.headers)
#         # cookies.update(response.cookies)
#         res = response.content.decode('utf-8')
#         if response.status_code == 503:
#             print('请求频繁,进行验证码验证中')
#             time.sleep(300)
#             res = ''
#     except:
#         res = ''
#     return res
#
# Download(url)
#
import base64
from urllib import parse

# url = "https://www.anjuke.com/captcha-verify/?callback=shield&from=antispam&serialID=49ce3060dcbf7ec9ffa20ea469380e78_54a6bd8879d144819589f17d734edcd8&history=aHR0cHM6Ly9zaGFuZ2hhaS5hbmp1a2UuY29tL3Byb3Avdmlldy9BMTY0NjM5MzcyOD9mcm9tPWZpbHRlciZzcHJlYWQ9Y29tbXNlYXJjaF9wJnRyYWRpbmdfYXJlYV9pZHM9NjI5OSZyZWdpb25faWRzPTEwJnBvc2l0aW9uPTI0MDMma3d0eXBlPWZpbHRlcg%3D%3D"
#
# # url = parse.unquote(url)
#
# str_l = "5aiH5aiH77yM5YW25a6e5oiR5b6I5Zac5qyi5L2g44CC"
# decode_str = base64.b64decode(str_l)
# print(decode_str.decode('utf-8'))

# str_l = base64.b64encode(url.encode('utf-8'))
# print(str_l)
# print(str_l.decode('utf-8'))
