#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from config import setting
import helper

db = setting.db_web

# 页面管理

url = ('/doct/diagnose')

PAGE_SIZE = 30

#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'DOCTOR_USE'):
            raise web.seeother('/')
        user_data=web.input(page='0')
        render = helper.create_render()

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  

        # 分页获取数据
        db_sku = db.pages.find({'first_page':1, 'available':1},
            sort=[('page_code', 1)],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE
        
        return render.diagnose(helper.get_session_uname(), helper.get_privilege_name(), db_sku,
            range(0, num))
