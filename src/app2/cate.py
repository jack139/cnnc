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

url = ('/app2/category')

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
    @app_helper.ex_check_sign(['app_id','tick','parent_id'], 'TNM')
    def POST(self):
        web.header('Content-Type', 'application/json')
        param = web.input(parent_id='')

        #print param
        
        data = []
        last_dir_id = ''
        last_dir_name = ''
        if param['parent_id']!='': # 准备显示目录页
            # 子目录
            real_parent_id = param.parent_id #app_helper.realid(param.parent_id) # 恢复原始id
            if real_parent_id is None:
                return json.dumps({'ret' : -4, 'msg' : '无效的parent_id'})

            db_obj=db.pages.find_one({'_id':ObjectId(real_parent_id)})
            if db_obj:
                if db_obj['page_type']!=1:
                    return json.dumps({'ret' : -5, 'msg' : '页面类型错误'})                    
                last_dir_id = str(db_obj['parent_id'])
                last_dir_name = db_obj['dir_name']

            data = get_list(real_parent_id, True)
        else:
            # 根目录
            data = get_list(param['parent_id'], False)

        ret_data = []

        for i in data:
            ret_data.append({
                'gid'       : str(i['_id']), #app_helper.randomid(i['_id']),
                #'parent_id' : app_helper.randomid(i['parent_id']) if i['parent_id']!='' else '',
                'type'      : i['page_type'], # 0 页面 1 目录 2 连接
                'title'     : i['dir_name'] if i['page_type']==1 else i['page_name'],
                'version'   : i['version'] if i.has_key('version') else i['dir_note'],
                #'start_node': app_helper.randomid(i['start_node']) if i['page_type']!=1 else '',
                'page_code' : i.get('page_code', '') if i['page_type']!=1 else '', # type==2 时没有 page_code
            })

        app_helper.log_app_api('external', 'category', param)

        # 返回
        return json.dumps({'ret' : 0, 'data' : ret_data })
