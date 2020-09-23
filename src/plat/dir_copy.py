#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
from libs import page_helper
import helper

db = setting.db_web

# 复制目录

url = ('/plat/dir_copy')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'DATA_MODIFY'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(page_id='', parent_id='')

        if user_data.page_id == '': 
            return render.info('参数错误！')  

        new_dir = page_helper.dir_copy(user_data.page_id)

        return render.info('成功完成！', '/plat/pages?parent_id='+user_data['parent_id'])

