import threading
import time
import requests

def IsSet():
    global num
    while True:
        if not event.isSet():
            try:
                proxyip = pi.getproxyip
            except:
                time.sleep(3)
                print("error")
                continue
            num +=1
            print(num)
            event.set()
        time.sleep(5)
        if not bol:
            break


class Getip(object):

    def __init__(self):
        self.order = 'ef8e072865d9e1afdd085731eb44f5d6'
        self.apiUrl = 'http://api.ip.data5u.com/dynamic/get.html?order=' + self.order
        self.res = ""

    @property
    def getproxyip(self):
        self.res = requests.get(self.apiUrl).text.strip()
        return self.res

if __name__ == '__main__':
    event = threading.Event()
    num = 0
    bol = True
    pi = Getip()
