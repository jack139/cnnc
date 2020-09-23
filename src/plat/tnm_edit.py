#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time,json
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 分期数据编辑

url = ('/plat/tnm_edit')

from app_settings import TNM_NAME
TNM_FACTS = TNM_NAME
#TNM_FACTS = ['T', 'N', 'M', 'G', 'L', 'S', 'Y', 'PSA', 'HE', 'RISK', 'HER2', 'ER', 'PR']

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'TNM_DATA'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(rule_id='')

        rule_data = { 'rule_id' : 'n/a' }
        stage_data = ''
        tnm_data = ''
        correct_data = []

        if user_data.rule_id != '': 
            db_obj=db.tnm.find_one({'_id':ObjectId(user_data.rule_id)})
            if db_obj!=None:
                # 已存在的obj
                rule_data = db_obj
                rule_data['rule_id']=rule_data['_id']

                # 处理分期因素数据
                tnm_data = rule_data['tnm']
                for x in TNM_FACTS:
                    if tnm_data.has_key(x):
                        continue
                    else: # 对后续添加的因素，旧的分期数据里可能会没有，例如RISK，2019-11-02
                        tnm_data[x] = []
                tnm_data = json.dumps(tnm_data)

                # 处理分期数据
                stage_data = rule_data.get('stage',[])

                for i in stage_data: # 处理逗号分隔
                    for x in TNM_FACTS:
                        if not i.has_key(x): # 对后续添加的因素，旧的分期数据里可能会没有，例如RISK，2019-11-02
                            i[x] = { 'rule' : 'or', 'val' : '' }
                        else:
                            i[x]['val'] = ','.join(i[x]['val'])
                stage_data = json.dumps(stage_data)

                # 纠错内容
                correct_data = db.correct.find({'node_id' : user_data.rule_id, 'status' : 'WAIT'})

        from app_settings import CANCER_CATEGORY
        cancer_category = sorted(CANCER_CATEGORY.items(), key=lambda s: s[1][0])

        return render.tnm_edit(helper.get_session_uname(), helper.get_privilege_name(), 
            rule_data, tnm_data, stage_data, cancer_category, correct_data)


    def POST(self):
        web.header('Content-Type', 'application/json')

        if not helper.logged(helper.PRIV_USER,'TNM_DATA'):
            return json.dumps({'ret':-1, 'msg':'没有权限'})

        param = web.input(rule_id='',tnm_name='',use_at='',tnm_rec='',stage_rec='',available='0',cancer_category='')

        print 'cancer_category', param['cancer_category']

        # 获取tnm数据， 过滤掉数据中 None
        tnm_rec = json.loads(param['tnm_rec'])
        for i in tnm_rec.keys():
            L = tnm_rec[i]
            tnm_rec[i] = sorted([x for x in L if x is not None], key=lambda s: s['weight'])

        #print tnm_rec

        # 准备校验，可用的编码
        availd_v = {}
        for x in TNM_FACTS:
            availd_v[x] = []
            for v in tnm_rec.get(x,[]): # 可用的值, 
                #availd_v[x].append(''.join(v['code'])) 
                # 最后一段要加上括弧 2019-11-02
                code = v['code'][0]+v['code'][1]+v['code'][2]+v['code'][3]+v['code'][4]
                code += '('+v['code'][5]+')' if v['code'][5]!='' else ''
                availd_v[x].append(code)
        print availd_v

        #  获取tnm数据，过滤掉数据中 None
        err_msg = ''
        stage_rec = json.loads(param['stage_rec'])
        for i in stage_rec: # 处理逗号分隔
            if i is None: # 在前端删除的会是None, 2019-11-02
                continue
            for x in TNM_FACTS:
                i[x]['val'] = [a.strip() for a in i[x]['val'].split(',') if a is not u'']

                #print i[x]['val']

                # 检查 stage 数据合法性
                for xx in i[x]['val']:
                    bingo = 0
                    for vv in availd_v[x]:
                        if vv.startswith(xx):
                            bingo = 1

                    if bingo==0:
                        err_msg += u'“%s”分期的“%s”列包含不可识别的编码“%s”；'%(i['name'], x, xx)

            i['weight'] = int(i['weight']) # 权重保持为整数， 2019-09-18

        stage_rec = sorted([x for x in stage_rec if x is not None], key=lambda s: s['weight'])

        # 包含不能识别的编码
        if len(err_msg)>0:
            return json.dumps({'ret':-9, 'msg':err_msg})

        #print stage_rec

        # 保存到数据库
        if param['rule_id']=='n/a': # 新建
            rule_id = None
            message = '新建'
        else:
            rule_id = ObjectId(param['rule_id'])
            message = '修改'

        try:
            update_set={
                'tnm_name'        : param['tnm_name'].strip(),
                'tnm_subname1'    : param['tnm_subname1'].strip(), # 2019/10/20
                'tnm_subname2'    : param['tnm_subname2'].strip(), # 2019/10/20
                'cancer_category' : param['cancer_category'].strip(), # 2019/10/20
                'version'         : param['version'].strip(),
                'weight'          : int(param['weight']),
                'grey'            : int(param.get('grey', '0')), # 是否置灰 2019/12/02
                'tnm'             : tnm_rec, 
                'stage'           : stage_rec,
                'use_at'          : param['use_at'].strip(),
                't_memo'          : param['t_memo'].strip(),
                'n_memo'          : param['n_memo'].strip(),
                'm_memo'          : param['m_memo'].strip(),
                'g_memo'          : param['g_memo'].strip(),
                'rich_text'       : param['rich_text'].strip(),
                'available'       : int(param['available']),
                'last_tick'       : int(time.time()),  # 更新时间戳
                'node_question'   : param['node_question']=="true",
                'ret_set'         : json.loads(param['ret_set']),
            }
        except ValueError:
            return json.dumps({'ret':-2, 'msg':'相应字段输入数字'})

        if rule_id is None:
            update_set['history'] = [(helper.time_str(), helper.get_session_uname(), message)]
            r2 = db.tnm.insert_one(update_set)
        else:
            db.tnm.update_one({'_id':rule_id}, {
                '$set'  : update_set,
                '$push' : {
                    'history' : (helper.time_str(), helper.get_session_uname(), message), 
                }  # 纪录操作历史
            })


        # 返回
        return json.dumps({'ret' : 0, 'msg' : '已保存'})
