#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
from bson.objectid import ObjectId
from config import setting
import app_helper

db = setting.db_web

url = ('/wx/tnm_check')

from app_settings import TNM_NAME
#TNM_NAME = ['T', 'N', 'M', 'G', 'L', 'S', 'Y', 'PSA', 'HE', 'RISK', 'HER2', 'ER', 'PR']

# - 根据输入的分期因素，返回下一个可用的分期因素列表，前端可置灰。 暂时弃用！
class handler:      
    def POST(self):
        web.header('Content-Type', 'application/json')
        param=web.input(session_id='', page_id='', tnm='') # tnm 只包含选择的那项分期因素

        print param

        if param.session_id=='':
            return json.dumps({'ret' : -1, 'msg' : 'session参数错误'})

        uname = app_helper.wx_logged(param.session_id)
        if uname is None:
            return json.dumps({'ret' : -2, 'msg' : '无效的session_id'})

        if param['page_id']=='':
            return json.dumps({'ret' : -3, 'msg' : '参数错误'})

        if param['tnm']=='':
            return json.dumps({'ret' : -5, 'msg' : '参数错误'})

        tnm = json.loads(param['tnm'])

        r1 = db.tnm.find_one({'_id': ObjectId(param['page_id'])},{ 'history' : 0 })
        if r1 is None:
            return json.dumps({'ret' : -4, 'msg' : '页面不可用！'})

        # 下一个可用分期因素
        ret_list = []

        tnm_name = tnm.get('tnm_name', '')
        tnm_code = tnm.get('tnm_code', '')

        if tnm_name in TNM_NAME:
            next_tnm = TNM_NAME[TNM_NAME.index(tnm_name)+1]

            for i in r1['stage']:
                if tnm_code in i[tnm_name]['val']:
                    ret_list.extend(i[next_tnm]['val'])

        print ret_list

        # 返回
        return json.dumps({'ret' : 0, 'data' : {
            'next_tnm'  : next_tnm,
            'next_list' : ret_list,
        }})

