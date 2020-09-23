#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
import json
from bson.objectid import ObjectId
from config import setting
import app_helper
from app_settings import CANCER_CATEGORY

db = setting.db_web

# 分期病种分类入口（根目录）

url = ('/app2/tnm_cate')

GEN_SIGN = {
    0 : '',
    1 : '● ',
    2 : '　► ',
    3 : '　　★ ',
    4 : '　　　◆ ',
}

# 返回有病种内容的大分类
def get_list(gen=0):
    cancer_category = sorted(CANCER_CATEGORY.items(), key=lambda s: s[1][0])

    data = []

    for cate in cancer_category:

        # 获取数据
        db_sku = db.tnm.find(
            {
                'available' : 1,
                'cancer_category' : cate[0]
            },
            { 
                'tnm_name' : 1,
                'version'  : 1,
            },
            sort=[ ('weight', 1) ],
        )

        if db_sku.count()>0:
            # 结果中添加 肿瘤分类名
            data.append({
                'type' : 'cancer_category',   # 目录项类型
                'name' : cate[1][1],
                'cate_id' : cate[0],
            })
        else:
            continue

        # 填充病种数据
        #tnm_names = []
        #
        #for i in db_sku:
        #    if i['tnm_name']+i['version'] in tnm_names: # 避免重复的病种名+版本，在后面展开， 2019-10-23
        #        continue
        #    else:
        #        tnm_names.append(i['tnm_name']+i['version']) # 保存病种名+版本， 
        #    i['gen'] = GEN_SIGN[gen]
        #    i['_id'] = str(i['_id']) # 为了json序列化
        #    i['type'] = 'cancer' # 目录项类型
        #    data.append(i)

    return data

# 按cate_id返回分类下的病种
def get_list2(cate_id, gen=1):

    data = []

    cate = CANCER_CATEGORY.get(cate_id)

    if cate is None: # cate_id 错误
        return data 

    # 获取数据
    db_sku = db.tnm.find(
        {
            'available' : 1,
            'cancer_category' : cate_id,
        },
        { 
            'tnm_name' : 1,
            'version'  : 1,
        },
        sort=[ ('weight', 1) ],
    )

    if db_sku.count()>0:
        # 结果中添加 肿瘤分类名
        #data.append({
        #    'type' : 'cancer_category_nolink',   # 目录项类型
        #    'name' : cate[1],
        #    'cate_id' : cate_id,
        #})
        pass
    else:
        # 无可用的病种数据
        return data

    # 填充病种数据
    tnm_names = []

    for i in db_sku:
        if i['tnm_name'] in tnm_names: # 避免重复的病种名，在后面展开， 2019-10-23
            continue
        else:
            tnm_names.append(i['tnm_name']) # 保存病种名， 
        #i['gen'] = GEN_SIGN[gen]
        #i['_id'] = str(i['_id']) # 为了json序列化
        #i['type'] = 'cancer' # 目录项类型
        data.append({
            'gid'     : str(i['_id']), #app_helper.randomid(i['_id']),
            'type'    : 'cancer',
            'name'    : i['tnm_name'],
            #'version' : i['version'],
        })

    return data

#  -------------------

class handler:  
    @app_helper.ex_check_sign(['app_id','tick','cate_id'], 'TNM') 
    def POST(self):
        web.header('Content-Type', 'application/json')
        param = web.input(cate_id='')

        #print param
        
        if param.cate_id=='':
            # 根目录
            data = get_list()
        else:
            data = get_list2(param.cate_id)


        app_helper.log_app_api('external', 'tnm_category', param)

        #print data 

        # 返回
        return json.dumps({'ret' : 0, 'data' : {
            'data' : data,
        }})
