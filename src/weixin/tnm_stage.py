#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
from bson.objectid import ObjectId
from config import setting
import app_helper

db = setting.db_web

url = ('/wx/tnm_stage')

from app_settings import TNM_NAME
#TNM_NAME = ['T', 'N', 'M', 'G', 'L', 'S', 'Y', 'PSA', 'HE', 'RISK', 'HER2', 'ER', 'PR']

# - 根据参数，结算分期
class handler:      
    def POST(self):
        web.header('Content-Type', 'application/json')
        param=web.input(session_id='', page_id='', tnm='')

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

        # 匹配分期数据
        ret_stage = None

        for i in r1['stage']:
            bingo = True
            for tnm_name in TNM_NAME:
                if not i.has_key(tnm_name): # 新的因素不在分期数据里，忽略
                    print 'PASS: ', tnm_name
                    continue

                print tnm_name, '---->', i[tnm_name]['val']
                # 分期数据为空
                if len(i[tnm_name]['val'])==0: 
                    print 'BLANK'
                    continue
                # ANY，不匹配，直接pass
                if i[tnm_name]['rule']=='any':
                    print 'ANY', i[tnm_name]['val']
                    continue
                # 完整匹配编码
                if tnm[tnm_name] in i[tnm_name]['val']:
                    print tnm[tnm_name], i[tnm_name]['val']
                    continue
                # 匹配前半部，例如 N2a 可 匹配 N2
                if True in [tnm[tnm_name][:len(v)] == v for v in i[tnm_name]['val']]:
                    print tnm[tnm_name], i[tnm_name]['val']
                    continue

                # 匹配前半部，例如 N2 可 匹配 N2a
                #if True in [tnm[tnm_name] == v[:len(tnm[tnm_name])] for v in i[tnm_name]['val']]:
                #    print tnm[tnm_name], i[tnm_name]['val']
                #    continue

                bingo = False
                break

            if bingo:
                ret_stage = i
                break

        if ret_stage is None:
            return json.dumps({'ret' : -9, 'msg' : '未匹配到分期！'})

        # 返回
        return json.dumps({'ret' : 0, 'data' : {
            'stage' : ret_stage['name'],
            'desc'  : ret_stage.get('desc',''),
        }})

