#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
from pymongo import MongoClient

#####
debug_mode = True   # Flase - production, True - staging
#####
#
enable_proxy = True
http_proxy = 'http://192.168.2.108:8888'
https_proxy = 'https://192.168.2.108:8888'
proxy_list = ['192.168.2.103']
enable_local_test = True
#####

db_serv_list='127.0.0.1'

cli = {
    'web'  : MongoClient(db_serv_list),
}

db_web = cli['web']['cnnc_db']
db_web.authenticate('ipcam','ipcam')

db_primary = db_web

tmp_path = '/tmp'
logs_path = '/usr/local/nginx/logs'
image_store_path = '/tmp/image/product'


app_host=''
wx_host=''
image_host='/static'
notify_host=''
app_pool=['']

WX_store = {
    '000' : { # 测试
        'wx_appid' : '',
        'wx_appsecret' : '',
        'mch_id' : '',
    },

}


# 微信设置
region_id = '000'
wx_setting = WX_store[region_id]

order_fuffix=''

http_port=8000
https_port=443

web.config.debug = debug_mode

config = web.storage(
    email = 'jack139@gmail.com',
    site_name = '',
    site_des = '',
    static = '/static'
)
