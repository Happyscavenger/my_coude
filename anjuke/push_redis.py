from pymongo import MongoClient
import json
from copy import deepcopy
import redis
import pymysql
import time

pool = redis.ConnectionPool(host='192.168.0.124', port=6379)
r = redis.Redis(connection_pool=pool)

client = MongoClient(
    'mongodb://root:Lansi123@dds-uf605bb40eca92541596-pub.mongodb.rds.aliyuncs.com:3717,dds-uf605bb40eca92542332-pub.mongodb.rds.aliyuncs.com:3717/admin?replicaSet=mgset-4720883')
my_db = client['anjuke']
my_col = my_db['house_col']

querylist = my_col.find()
for i in querylist:
    print(i)
    # houseid = i['houseid']
    # my_col.update_one({'houseid':'{}'.format(houseid)},{"$set":{'tag':1}})
    item={}
    item['href'] = i['href']
    item['title'] = i['title']
    item['houseid'] = i['houseid']
    items = json.dumps(deepcopy(item))
    conn = pymysql.connect(
        host='rm-uf6t4r3u8vea8u3404o.mysql.rds.aliyuncs.com',
        port=3306,
        user='caijisa',
        passwd='Caijisa123',
        db='lansi_data_collection',
        charset='utf8')
    cursor = conn.cursor()
    sql = "SELECT `{}` FROM `lansi_data_collection`.`fangtianxia` where `source`='安居客'".format(item['href'])
    cursor.execute(sql)
    result = cursor.fetchone()
    if result is not None:
        print(result)
    else:
        r.sadd("item", items)
    time.sleep(0.2)
print('数据拉取完成')
