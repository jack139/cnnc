#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
from bson.objectid import ObjectId
from config import setting
import app_helper

db = setting.db_web

url = ('/wx/tnm_page')

# - TNM 页面
class handler:      
    def POST(self):
        web.header('Content-Type', 'application/json')
        param=web.input(session_id='', page_id='', only_one='')

        print param

        if param.session_id=='':
            return json.dumps({'ret' : -1, 'msg' : 'session参数错误'})

        uname = app_helper.wx_logged(param.session_id)
        if uname is None:
            return json.dumps({'ret' : -2, 'msg' : '无效的session_id'})

        if param['page_id']=='':
            return json.dumps({'ret' : -3, 'msg' : '参数错误'})

        r1 = db.tnm.find_one({'_id': ObjectId(param['page_id'])},{ 'history' : 0 })
        if r1 is None:
            return json.dumps({'ret' : -4, 'msg' : '页面不可用！'})

        r1['_id'] = str(r1['_id'])

        ret_data = ret_count = None

        # 如果only_one==1，直接返回此页面内容，否则检查是否有同名病种，生成多个入口
        if param.only_one=='1':
            # 返回
            ret_data = r1
            ret_count = 1
        else:
            r2 = db.tnm.find(
                {
                    'available' : 1,
                    'tnm_name'  : r1['tnm_name'],
                    #'version'   : r1['version'],
                },
                { 
                    'tnm_name'     : 1,
                    'tnm_subname1' : 1,
                    'tnm_subname2' : 1,
                    'use_at'       : 1,
                    'version'      : 1,
                },
                sort=[ ('weight', 1) ]
            )
            if r2.count()==1:  # 只有一个病种
                # 返回
                ret_data = r1
                ret_count = 1
            else:
                ret_data = []
                for x in r2:
                    ret_data.append({
                        '_id'          : str(x['_id']),
                        'tnm_name'     : x['tnm_name'],
                        'tnm_subname1' : x['tnm_subname1'],
                        'tnm_subname2' : x['tnm_subname2'],
                        'use_at'       : x['use_at'],
                        'version'      : x['version'],
                    })

                # 返回 多个入口
                ret_count = r2.count()

        #print ret_data
        print ret_count

        return json.dumps({'ret' : 0, 'data' : {
            'data'     : ret_data,
            'only_one' : ret_count,
        }})
