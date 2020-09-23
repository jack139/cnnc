#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

urls = [
    '/wx/',         'First',

    #'/wx/init_signup',    'InitSignup',
    #'/wx/signup_init',    'Signup',

    '/wx/init_cate',    'InitCate',

    '/wx/init_cate2',    'InitCate2',
    '/wx/cate2_init',    'Cate2',

    '/wx/init_doct',    'InitDoct',
    '/wx/doct_init',    'Doct',

    '/interface4wechat/cnnc_category',    'InitCate3',  # 对外weixin接入
    '/interface4app/cnnc_category',    'Cate2',  # 对外app接入

    '/interface4wechat/tnm_category',    'InitTNMCate2',  # 对外weixin接入
    '/interface4app/tnm_category',    'TNMCate',  # 对外app接入

    '/wx/init_tnm_cate',    'InitTNMCate',
    '/wx/tnm_cate_init',    'TNMCate',

    '/wx/init_tnm',    'InitTNMPage',
    '/wx/tnm_init',    'TNMPage',

    '/wx/signature',    'WxSignature',
]

## ---- 分布式部署---------------------------------
app_dir = ['weixin', 'ui']
app_list = []
for i in app_dir:
    tmp_list = ['%s.%s' % (i,x[:-4])  for x in os.listdir(i) if x[:2]!='__' and x.endswith('.pyc')]
    app_list.extend(tmp_list)
#print app_list

for i in app_list:
    # __import__('pos.audit', None, None, ['*'])
    tmp_app = __import__(i, None, None, ['*'])
    if not hasattr(tmp_app, 'url'):
        print tmp_app
        continue
    urls.extend((tmp_app.url, i+'.handler'))

# 最后一个
#urls.extend(('/([0-9|a-z]{24})', 'weixin.wxurl.handler')) #/([0-9|a-z]{24})   /(.+)

#print urls
#-----------------------------------------------------
