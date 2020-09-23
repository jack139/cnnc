#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 病种分类入口（根目录）

url = ('/ui/cate')

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
        if i.get('page_type')==1: # 目录
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
    def GET(self):
        from wx import get_param, init_job, genSignature

        if not helper.logged(helper.PRIV_USER, 'DATA_MODIFY'):
            raise web.seeother('/')

        user_data=web.input(parent_id='')

        print user_data
        
        session_id = None

        if user_data.has_key('code'):  # 来自微信
            param = get_param(user_data)
            if user_data.get('session_id','')=='':
                session_id = init_job(user_data.code)
                if session_id==None:
                    raise web.seeother('/wx/init_cate?%s' % param)
            else:
                session_id = user_data['session_id']

            url = 'http://'+web.ctx.environ['REQUEST_URI']
            signature = genSignature(url)

        #user_data=web.input(parent_id='')
        render = helper.create_render(plain=True, force_visitor=True)

        data = []
        last_dir_id = ''
        last_dir_name = ''
        if user_data['parent_id']!='': # 准备显示目录页
            # 子目录
            db_obj=db.pages.find_one({'_id':ObjectId(user_data.parent_id)})
            if db_obj:
                last_dir_id = str(db_obj['parent_id'])
                last_dir_name = db_obj['dir_name']

            data = get_list(user_data['parent_id'], True)
        else:
            # 根目录
            data = get_list(user_data['parent_id'], False)

        
        #return render.ui_cate(data, user_data['parent_id'], last_dir_id, last_dir_name, session_id, signature)
        return render.ui_cate(data, user_data['parent_id'], last_dir_id, last_dir_name)
