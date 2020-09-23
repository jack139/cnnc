#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, copy
import app_helper
#from config import setting

db = app_helper.db  # 默认db使用web本地


# 返回用户信息
def get_user_info(user_id, q_type='uname', need_return=None):
    print 'get_user_info()'
    if q_type not in ['uname', 'openid', 'both']:
        return None
    if q_type=='both':
        condition = {
            '$or' : [ 
                {'uname':user_id},
                {'openid':user_id}
            ]
        }
    else:
        condition = {q_type: user_id}

    r=db.app_user.find_one(condition, projection=need_return)

    # 返回的 r 由两部分数据拼接而成
    return r

def update_user_info(user_id, q_type='uname', update_set=None):
    print 'update_user_info()'
    if q_type not in ['uname', 'openid']:
        return None

    if not isinstance(update_set, dict):
        return None

    r = db.app_user.update_one({q_type: user_id}, {'$set':update_set})
    return r


# 新建用户信息
def new_user_info(user_id, q_type='uname', update_set=None):
    print 'new_user_info()'
    if q_type not in ['uname', 'openid']:
        return None

    if not isinstance(update_set, dict):
        return None

    update_set[q_type] = user_id

    r = db.app_user.insert_one(update_set)

    return r


