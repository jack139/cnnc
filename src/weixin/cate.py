#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
import json
from bson.objectid import ObjectId
from config import setting
import app_helper

db = setting.db_web

# 病种分类入口（根目录）

url = ('/wx/cate')

GEN_SIGN = {
    0 : '',
    1 : '●',
    2 : '　►',
    3 : '　　★',
    4 : '　　　◆',
}

def get_list(parent_id, deepin=False, gen=0):
    print parent_id, deepin, gen
    # 获取数据
    db_sku = db.pages.find(
        {
            'parent_id' : parent_id,
            'available' : 1,
        },
        { 'history' : 0 },
        sort=[ ('weight', 1), ('page_type', -1) ],
    )

    data = []

    for i in db_sku:
        i['gen'] = GEN_SIGN[gen]
        i['_id'] = str(i['_id']) # 为了json序列化
        if i.get('page_type')==1: # 目录
            if i.get('dir_name')==u'筛查': # 筛查单列，不在指南目录里列出 2020-04-26
                continue
            data.append(i)
            if deepin:
                data.extend(get_list(str(i['_id']), deepin=True, gen=gen+1))
        elif i.get('page_type')==2: # 页面链接
            r2 = db.pages.find_one({'page_code':i['link_page_code'], 'page_type':0}, { 'history' : 0 })
            if r2:
                i['link_page_id'] = str(r2['_id'])
                data.append(i)
        else:
            data.append(i)

    return data

#  -------------------
class handler:  
    def POST(self):
        web.header('Content-Type', 'application/json')
        param = web.input(session_id='', parent_id='')

        print param
        
        if param.session_id=='':
            return json.dumps({'ret' : -1, 'msg' : 'session参数错误'})

        uname = app_helper.wx_logged(param.session_id)
        if uname is None:
            return json.dumps({'ret' : -2, 'msg' : '无效的session_id'})


        data = []
        last_dir_id = ''
        last_dir_name = ''
        if param['parent_id']!='': # 准备显示目录页
            # 子目录
            deepin = True
            db_obj=db.pages.find_one({'_id':ObjectId(param.parent_id)})
            if db_obj:
                if db_obj.get('dir_name')==u'筛查': # 筛查单列，文件夹作为根目录 2020-04-26
                    deepin = False
                    # 记录点击
                    app_helper.click_inc()
                else:
                    last_dir_id = str(db_obj['parent_id'])
                    last_dir_name = db_obj['dir_name']

            data = get_list(param['parent_id'], deepin)
        else:
            # 根目录
            data = get_list(param['parent_id'], False)
            # 记录点击
            app_helper.click_inc()

        for i in data:
            i['rich_text'] = ''

        # 返回
        return json.dumps({'ret' : 0, 'data' : {
            'data'          : data,
            'parent_id'     : param['parent_id'],
            'last_dir_id'   : last_dir_id,
            'last_dir_name' : last_dir_name
        }})
