#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
from bson.objectid import ObjectId
from config import setting
import app_helper
from app_settings import TNM_NAME

db = setting.db_web

url = ('/app2/tnm_page')

# - TNM 页面
class handler:      
    @app_helper.ex_check_sign(['app_id','tick','page_id','only_one'], 'TNM') 
    def POST(self):
        web.header('Content-Type', 'application/json')
        param=web.input(page_id='', only_one='')

        #print param

        if param['page_id']=='':
            return json.dumps({'ret' : -4, 'msg' : '参数错误'})

        #r1 = db.tnm.find_one({'_id': ObjectId(app_helper.realid(param['page_id']))},{ 'history' : 0 })
        r1 = db.tnm.find_one({'_id': ObjectId(param['page_id'])},{ 'history' : 0 })
        if r1 is None:
            return json.dumps({'ret' : -5, 'msg' : '分期不存在'})

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
                        'gid'          : str(x['_id']), #app_helper.randomid(x['_id']),
                        'name'         : x['tnm_name'],
                        'subname1'     : x['tnm_subname1'],
                        'subname2'     : x['tnm_subname2'],
                        'use_at'       : x['use_at'],
                        'version'      : x['version'],
                    })

                # 返回 多个入口
                ret_count = r2.count()

        if ret_count==1:
            x = ret_data

            # 清理tnm因素数据
            for i in x['tnm'].keys():
                if len(x['tnm'][i])==0:
                    #print 'tnm pop: ', i
                    x['tnm'].pop(i, None)
                else:
                    for j in x['tnm'][i]:
                        j['code'] = ''.join(j['code'])

            # 清理分期数据
            for i in x['stage']:
                for j in TNM_NAME:
                    if i.has_key(j) and len(i[j]['val'])==0:
                        #print 'stage pop: ', j
                        i.pop(j, None)
                    elif i.has_key(j) and i[j]['rule'].lower()!='any':  # 旧数据会有and, 都替换为 or
                            i[j]['rule'] = 'or'

                i.pop('desc', None) # 不返回desc说明信息

            ret_data = {
                'gid'      : str(x['_id']), #app_helper.randomid(x['_id']),
                'name'     : x['tnm_name'],
                'subname1' : x['tnm_subname1'],
                'subname2' : x['tnm_subname2'],
                'version'  : x['version'],
                'use_at'   : x['use_at'],
                'facts'    : x['tnm'], # 影响因素
                'stages'   : x['stage'], # tnm分期
            }


        app_helper.log_app_api('external', 'tnm_page', param)

        #print ret_data
        print ret_count

        return json.dumps({'ret' : 0, 'data' : {
            'page_data' : ret_data,
            'only_one'  : ret_count,
        }})
