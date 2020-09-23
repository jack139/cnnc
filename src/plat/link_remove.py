#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
#from libs import pos_func
import helper

db = setting.db_web

# 删除页面链接

url = ('/plat/link_remove')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'DATA_MODIFY'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(page_id='', parent_id='')

        if user_data.page_id == '': 
            return render.info('参数错误！')  

        db.pages.delete_one({'_id':ObjectId(user_data.page_id), 'page_type':2})

        return render.info('成功删除！', '/plat/pages?parent_id='+user_data['parent_id'])

