#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web, json
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

url = ('/ui/doct')

# - 规则树页面
class handler:      
    def GET(self):
        render = helper.create_render(plain=True, force_visitor=True)
        param=web.input(page_id='', page_code='')

        if param['page_id']=='' and param['page_code']=='':
            return render.ui_info('参数错误！')  

        if len(param['page_code'])>0:
            r1 = db.pages.find_one({
                'page_code' : param['page_code'].upper(),
                #'page_type' : 0,
                'available' : 1
            }, { 'history' : 0 })
            if r1 is None:
                r1 = db.pages.find_one({
                    'page_code' : param['page_code'].upper()+'#1',  # 加 '#1' 再试一次
                    #'page_type' : 0,
                    'available' : 1
                }, { 'history' : 0 })
                if r1 is None:
                    return render.ui_info('页面不可用！')  
        else:
            r1 = db.pages.find_one({'_id': ObjectId(param['page_id'])},{ 'history' : 0 })
            if r1 is None:
                return render.ui_info('页面不可用！')  

        r2 = db.nodes.find_one({'_id':ObjectId(r1['start_node'])})
        if r2 is None:
            return render.ui_info('页面数据错误！')  

        if len(r2.get('child',[]))>0:
            return render.doct_ui(r1)  # 显示规则树
        else:
            return render.ui_text(r1)  # 显示纯文本

