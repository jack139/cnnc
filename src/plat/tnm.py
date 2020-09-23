#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 分期数据列表

url = ('/plat/tnm')

PAGE_SIZE = 30

#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'TNM_DATA'):
            raise web.seeother('/')
        user_data=web.input(page='0', tnm_name='')
        render = helper.create_render()

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  

        conditions ={}

        tnm_name = user_data.tnm_name.strip()
        if tnm_name!='':
            conditions = {
                '$or' : [
                    {'tnm_name'  : { '$regex' : u'%s.*'%(tnm_name.replace('*','\\*').replace('?','\\?')), '$options' : 'i' }},
                    {'tnm_subname1'  : { '$regex' : u'%s.*'%(tnm_name.replace('*','\\*').replace('?','\\?')), '$options' : 'i' }},
                    {'tnm_subname2'  : { '$regex' : u'%s.*'%(tnm_name.replace('*','\\*').replace('?','\\?')), '$options' : 'i' }},
                ]
            }

        from app_settings import CANCER_CATEGORY
        cancer_category = CANCER_CATEGORY.copy()
        cancer_category[''] = (0,'-')

        # 分页获取数据
        db_sku = db.tnm.find(conditions,
            sort=[ ('available', -1), ('cancer_category', 1), ('weight', 1) ],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE
        
        return render.tnm(helper.get_session_uname(), helper.get_privilege_name(), db_sku,
            range(0, num), tnm_name, int(user_data['page']), cancer_category)
