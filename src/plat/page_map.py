#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
from config import setting
from bson.objectid import ObjectId
import helper

db = setting.db_web

# 编辑页面规则，与js交互
url = ('/plat/page_map')


# 从文字中取页面编码
def get_page_id(c0):
    c = c0.encode('utf-8') # 使用utf-8处理，unicode时isalnum()会判断错误， 2018-08-25
    pos = c.find('@') + 1

    if pos==0: # 未找到@
        return None

    page_id = ''
    for x in c[pos:]:
        if x.isalnum() or x=='-':  # 页面编码只包含字母、数字和减号('-')
            page_id += x
        else:
            break

    if len(page_id)==0:
        return None

    print 'PAGE_ID', page_id
    return page_id.upper()


class handler:        
    def GET(self):
        if not helper.logged(helper.PRIV_USER,'DATA_MODIFY'):
            raise web.seeother('/')

        render = helper.create_render(plain=True)
        param=web.input(page_id='')

        r1 = db.pages.find_one({'_id': ObjectId(param['page_id'])})
        if r1 is None:
            return json.dumps({'ret':-2, 'msg':'page_id参数错误'})

        #r2 = db.nodes.find({'page_id':param['page_id']})

        #data=[x for x in r2]
        data = []

        return render.page_map(helper.get_session_uname(), helper.get_privilege_name(), 
            data, param['page_id'], r1['page_code'], r1['page_name'])


    def POST(self):
        web.header("Content-Type", "application/json")
        if not helper.logged(helper.PRIV_USER, 'DATA_MODIFY'):
            return json.dumps({'ret':-1,'msg':'无访问权限'})

        param = web.input(page_id='', element_data='', link_data='')

        if '' in (param.page_id, param.element_data, param.link_data):
            return json.dumps({'ret':-1, 'msg':'参数错误'})

        element_data = json.loads(param.element_data)
        link_data = json.loads(param.link_data)

        #print element_data
        #print link_data

        r1 = db.pages.find_one({'_id': ObjectId(param['page_id'])})
        if r1 is None:
            return json.dumps({'ret':-2, 'msg':'page_id参数错误'})

        # 处理节点
        #{
        #    u'original_text': u'See Suggested Regimens (MANT-A)', 
        #    u'angle': 0, 
        #    u'inPorts': [u'i'], 
        #    u'id': u'cc2b347f-3f6d-470b-b93c-16602765f657', 
        #    u'node_id': u'x5', 
        #    u'outPorts': [u'o'], 
        #    u'attrs': {
        #        u'.label': {u'text': u'See\nSuggested\nRegimens\n(MANT-A)', u'ref-y': 5}
        #    }, 
        #    u'position': {u'y': 202, u'x': 245}, 
        #    u'z': 9, 
        #    u'type': u'devs.Atomic', 
        #    u'ports': {
        #            u'items': [{u'group': u'in', u'id': u'i', u'attrs': {u'.port-label': {u'text': u'i'}}}, 
        #                        {u'group': u'out', u'id': u'o', u'attrs': {u'.port-label': {u'text': u'o'}}}], 
        #            u'groups': {u'out': {u'position': {u'name': u'right'}, u'attrs': {u'.port-label': {u'fill': u'#000'}, 
        #            u'.port-body': {u'magnet': True, u'stroke': u'#000', u'r': 10, u'fill': u'#fff'}}, 
        #            u'label': {u'position': {u'args': {u'y': 10}, u'name': u'right'}}}, u'in': {u'position': {u'name': u'left'}, 
        #            u'attrs': {u'.port-label': {u'fill': u'#000'}, u'.port-body': {u'magnet': True, u'stroke': u'#000', 
        #            u'r': 10, u'fill': u'#fff'}}, u'label': {u'position': {u'args': {u'y': 10}, u'name': u'left'}}}}
        #    }, 
        #    u'size': {u'width': 80, u'height': 66}
        #}


        alert_msg = ''

        start_node = None
        nodes_dict = {} # 用于添加链接时查询
        node_list = [] # 记录所有节点的ObjectId，用于检查删除的节点

        # >>>>>>>>>>>>>>> 此循环处理中不可以跳出返回，否则会数据保存不完整 <<<<<<<<<<<<<<
        for i in element_data: # 
            #print i

            original_text = i['original_text'].strip()

            if original_text=='0': # 起始节点
                start_node = i['node_id']

            node_type = 0 if original_text in ['0', '*', '+'] else 1


            if '@' in original_text: # 检查是否存在调转
                jump_to_page = get_page_id(original_text)
                if jump_to_page:
                    r5 = db.pages.find_one({'page_code': jump_to_page})
                    if r5 is None:
                        alert_msg += (u'跳转的页面（%s）不存在！<br>'%jump_to_page)
                    else:
                        if str(r5['_id'])==param['page_id']: # 检查是否跳到自己
                            original_text = '@未知页面'
                            alert_msg += (u'不能跳转到当前页面（%s）！<br>'%jump_to_page)
                    
                    original_text = original_text.upper()  # 跳转页面全部大写

                    if original_text[0]=='@': # 是否是调转节点
                        node_type = 0 # 调整节点也是虚节点

            # 处理纠错结果 # 2019-02-12
            node_question = i.get('node_question', {'check':False, 'correct':[]})

            # 节点更新内容
            node = {
                'page_id'   : param['page_id'],
                'node_type' : node_type,
                'parent'    : [],
                'child'     : [],
                'text'      : original_text,
                #'node_id'   : i['node_id']
                'position'  : i['position'],  # 记录节点在页面的位置，方便复原
                'node_prop'     : i.get('node_prop',''), # 节点属性 2018－08-14
                'node_weight'   : i.get('node_weight','1'), # 节点权重 2018－08-14
                'node_question' : node_question['check'], # 2019-02-12
            }

            if i['node_id']=='': #说明是新节点
                r3 = db.nodes.insert_one(node)
                node['_id'] = r3.inserted_id
                print 'NEW: ', str(r3.inserted_id)
            else:
                r2 = db.nodes.update_one({'_id':ObjectId(i['node_id'])}, {'$set': node}, upsert=True)
                if r2.upserted_id is not None: # 更新时插入
                    node['_id'] = r2.upserted_id
                    print 'UPSERT: ', str(r2.inserted_id)
                else:
                    node['_id'] = ObjectId(i['node_id'])

                # 更新纠错记录状态
                if node_question['check']==False and len(node_question['correct'])>0:
                    db.correct.update_many({'node_id' : i['node_id'], 'status' : 'WAIT'}, {'$set' : {'status' : 'PASS'}})

            nodes_dict[i['id']] = node

            node_list.append(node['_id'])

            #print node

        # 处理连接
        #{
        #    u'target': {
        #        u'id': u'c802b6c6-a694-4b18-aa3a-6dfa436f8637', 
        #        u'port': u'i'
        #    }, 
        #    u'vertices': [
        #        {u'y': 112, u'x': 136}, 
        #        {u'y': 114, u'x': 232}
        #    ], 
        #    u'source': {
        #        u'id': u'bac2de56-266c-4428-9096-29f46d172ead', 
        #        u'port': u'o'
        #    }, 
        #    u'attrs': {
        #        u'.marker-target': {u'd': u'M 10 0 L 0 5 L 10 10 z', u'fill': u'#4B4F6A'}
        #    }, 
        #    u'z': 3, 
        #    u'type': u'devs.Link', 
        #    u'id': u'fdf956b4-159a-4776-bd2b-cc9824ab8f28'
        #}

        db.connect.remove({'page_id' : param['page_id']}) # 先删除所有连线
        for i in link_data:
            nodes_dict[i['target']['id']]['parent'].append(str(nodes_dict[i['source']['id']]['_id']))
            nodes_dict[i['source']['id']]['child'].append(str(nodes_dict[i['target']['id']]['_id']))
            db.connect.insert_one({ # 保存连线数据
                'page_id'  : param['page_id'],
                'source'   : str(nodes_dict[i['source']['id']]['_id']),
                'target'   : str(nodes_dict[i['target']['id']]['_id']),
                'vertices' : i.get('vertices',[])
            })

        # 更新到db
        for i in nodes_dict.values():
            db.nodes.update_one({'_id':i['_id']}, {'$set':i})

        # 删除页面中未更新的，说明这次删除的
        r4 = db.nodes.find({'page_id' : param['page_id']})
        for i in r4:
            if i['_id'] not in node_list:
                print 'REMOVE: ', str(i['_id'])
                db.nodes.delete_one({'_id':i['_id']})

        # 更新页面起始节点
        db.pages.update_one({'_id': ObjectId(param['page_id'])}, {
            '$set'  : {'start_node': start_node},
            '$push' : {'history' : (helper.time_str(), helper.get_session_uname(), '保持规则树') }
        })

        if alert_msg=='':
            return json.dumps({'ret':0,'msg':'成功保存'})
        else:
            return json.dumps({'ret':1,'msg':alert_msg})


