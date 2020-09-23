#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# 前端代码 公用变量及函数

import time, os, hashlib, base64
import urllib, urllib3, json
import functools
import re
import web
from config import setting

#---------------------------- 标记是否在测试／staging环境，用于区别生成环境的一些设置
IS_TEST = 'dev' in setting.app_host
IS_STAGING = 'dev' in setting.app_host
#----------------------------

if IS_TEST:
    from app_settings_test import * 
elif IS_STAGING:
    from app_settings_stag import * 
else:
    from app_settings import * 

db = setting.db_web

# 时间函数
ISOTIMEFORMAT=['%Y-%m-%d %X', '%Y-%m-%d', '%Y%m%d%H%M', '%Y-%m-%d %H:%M']

def time_str(t=None, format=0):
    return time.strftime(ISOTIMEFORMAT[format], time.localtime(t))

def validateEmail(email):
    if len(email) > 7:
      if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
          return 1
    return 0

RAND_BASE=[
    'abcdefghijklmnopqrstuvwxyz',
    '0123456789',
]

def my_crypt(codestr):
    return hashlib.sha1("sAlT139-"+codestr.encode('utf-8')).hexdigest()

def my_rand(n=4, base=0):
    import random
    return ''.join([random.choice(RAND_BASE[base]) for ch in range(n)])


# 内部使用号码，固定验证码, 2015-12-22, gt
INNER_NUM = {
    #'18516569412' : '9998',
}



#==========================================================================


BLOCK_LIST = [
#    '15000623214',
]



# 查询session
def get_session(session_id):
    r = db.app_sessions.find_one({'session_id':session_id})
    if r and time.time()-r['attime']>1800: # 半小时更新一次, 减少更新session次数
        db.app_sessions.update_one({'session_id':session_id},{'$set':{'attime':time.time()}})
    return r

# 检查session登录状态
def logged(session_id):
    session = get_session(session_id)
    if session==None:
        return None
    else:
        if session['login']==1: # 登录后返回uname
            return session['uname']
        else:
            return None

# 检查session登录状态, 合并app与微信订单
def app_logged(session_id):
    session = get_session(session_id)
    if session==None:
        return None
    else:
        if session.get('login')==1 and session.get('bind')==1: # 要求 登录 且 绑定
            return {
                'uname'  : session['uname'], 
                'userid' : session['userid'],  
                'type'   : session.get('type',1),
                'mice'   : session.get('mice',0),
            }
        else:
            return None

# 检查openid
def check_openid(openid):
    #r = db.app_user.find_one_and_update(
    #    {'openid' : openid},
    #    {'$set'   : {'last_time' : time_str()}},
    #    {'uname' : 1, 'openid':1}
    #)
    #if r:
    #    return {'uname' : r.get('uname',''), 'openid': r['openid']}
    #else:
        return None

# 微信检查session登录状态
def wx_logged(session_id):
    session = get_session(session_id)
    if session==None:
        return None
    else:
        #db.app_user.update_one({'uname' : session['uname']},{
        #   '$set'  : {'last_time' : time_str()}
        #})
        if session['login']==1: # 登录后返回uname
            #return session['uname']
            return {
                'openid' : session['openid'], 
                'unionid': session.get('unionid',''),
                'userid' : session.get('userid', ''),  
                'type'   : session.get('type',3),
                'mice'   : session.get('mice',0),
            }
        else:
            return None

def generate_sign(c): # c时列表，c[0]一定是app_id
    db_dev = db.app_device.find_one({'app_id' : c[0]}, {'private_key':1})
    if db_dev==None:
        return None
        #return json.dumps({'ret' : -3, 'msg' : 'app_id错误'})
    else:
        #验证签名
        sign_str = '%s%s' % (db_dev['private_key'], ''.join(i for i in c))
        #print sign_str.encode('utf-8')
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()




# 生成 order_trade_id
def get_new_order_id(version='v1', prefix=''):
    if IS_TEST or IS_STAGING:
        surfix = '-test'
    else:
        surfix = ''

    # 检查订单号唯一性
    cc=1
    while cc!=None:
        # order_trade_id 城市(1位)+日期时间(6+4位)+随机数(6位)+版本
        order_trade_id = '%s20%s%s%s%s' % (prefix,time_str(format=2)[2:],my_rand(6,1),version[-1],surfix)
        if prefix=='d': # 充值订单
            cc = db.order_recharge.find_one({'recharge_id' : order_trade_id},{'_id':1})
        else: # 交易流水
            cc = db.order_trade.find_one({'order_trade_id' : order_trade_id},{'_id':1})

    if prefix=='d': # 充值订单, 先占位 2016-06-27,gt
        db.order_recharge.insert_one({'recharge_id':order_trade_id}) # 
    else:
        db.order_trade.insert_one({'order_trade_id':order_trade_id}) # 先占位 2016-03-17,gt
    return order_trade_id


# 生成userid
def gen_new_userid():
    cc=1
    while cc is not None:
        # userid 日期时间(6+4位)+随机数(5位)
        userid_0 = '%s%s' % (time_str(format=2)[2:],my_rand(6,1))
        userid = hashlib.md5(userid_0).hexdigest().upper()
        cc = db.app_user.find_one({'userid' : userid},{'_id':1})
    db.app_user.insert_one({'userid':userid}) # 先占位 2016-03-17,gt
    return userid


# 取得设备类型
def get_devive_type(app_id):
    db_dev = db.app_device.find_one({'app_id':app_id},{'type':1})
    if db_dev:
        return db_dev['type']
    else:
        return ''


# 获取access_token，与wx.py 中相同
def get_token(force=False, region_id=None): # force==True 强制刷新
    if region_id==None:
        region_id = setting.region_id
    print 'region: ', region_id
    if not force:
        db_ticket = db.jsapi_ticket.find_one({'region_id':region_id})
        if db_ticket and int(time.time())-db_ticket.get('token_tick', 0)<3600:
            if db_ticket.get('access_token', '')!='':
                print db_ticket['access_token']
                return db_ticket['access_token']

    url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % \
        (setting.WX_store[region_id]['wx_appid'], setting.WX_store[region_id]['wx_appsecret'])
    f=urllib.urlopen(url)
    data = f.read()
    f.close()

    t=json.loads(data)
    if t.has_key('access_token'):
        print t
        db.jsapi_ticket.update_one({'region_id':region_id},
            {'$set':{'token_tick':int(time.time()), 'access_token':t['access_token']}},upsert=True)
        return t['access_token']
    else:
        db.jsapi_ticket.update_one({'region_id':region_id},
            {'$set':{'token_tick':int(time.time()), 'access_token':''}},upsert=True)
        return ''

### ------------用于外部用户的app_id----------------------------------------------

CNNC_APP_IDs = { # 外部用户app_id, private_key # 用于 app中接口
    'SXZMSGIS' : '28A7554DD8F644332A06A982F00F80CB9FDF988E', #'内部测试',
}

TNM_APP_IDs = { # 外部用户app_id, private_key  # 用于 app中接口， 和app2
    'SXZMSGIS' : '28A7554DD8F644332A06A982F00F80CB9FDF988E', #'内部测试',
}

def ex_generate_sign(c, app_id_type): # c时列表，c[0]一定是app_id
    if app_id_type=='CNNC':
        APP_IDs = CNNC_APP_IDs
    elif app_id_type=='TNM':
        APP_IDs = TNM_APP_IDs
    else:
        return None

    if c[0] not in APP_IDs.keys():
        return None
    else:
        #验证签名
        sign_str = '%s%s' % (APP_IDs[c[0]], ''.join(i for i in c))
        #print sign_str.encode('utf-8')
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

### ----------------------------------------------------------------------------------------------------
###    用于请求签名验证的修饰器  ---- 外部用户
###
###    @param sign_names 需要参与签名的参数名列表
###        需要按顺序, sign_names[0]为app_id
###    @param param_defaults 非必须的参数
### ----------------------------------------------------------------------------------------------------
def ex_check_sign(param_names, app_id_type='CNNC'):
    def _wrap(func):
        @functools.wraps(func)
        def __wrap(*args, **kw):
            # 获取参数, 缺少必须参数返回错误
            defaults = dict((el,'') for el in param_names)
            try:
                param = web.input('app_id', 'tick', 'sign', **defaults)
            except:
                print web.input()
                return api_error(-2, '缺少参数')

            print param

            # 验证签名,验证失败返回错误
            sign_data = [param[name] for name in param_names]
            #print sign_data
            md5_str = ex_generate_sign(sign_data, app_id_type)
            if md5_str != param.sign:
                print '------> 签名验证错误 in check_sign'
                print md5_str, param.sign
                return api_error(-1, '签名验证错误')

            try:
                if abs(int(param.tick)-int(time.time()))>300: # 时间戳是否再5分钟之内
                    xx = int('a') # 故意落入下面exception
            except ValueError:
                return api_error(-3, '时间戳不是当前时间')

            return func(*args, **kw)
        return __wrap
    return _wrap


# 用于返回api 错误信息 
def api_error(ret, msg=''):
    # 防止web.py的影响
    web.ctx.status = '200 OK'
    web.ctx.headers = [('Content-Type', 'application/json')]

    return json.dumps({'ret': ret, 'msg': msg})

# 生成图片库的url
def image_url(image_name):
    return 'https://%s/image/product/%s/%s'%(setting.image_host, image_name[:2], image_name)


# 保存图片, 用于接口上传的图片, 图片数据是base64格式
def write_image(image_type, img_data): # 图片按随机文件名散列存放
    image_name = my_rand(12) + '.' + image_type.lower()
    data = base64.decodestring(img_data)
    to_path='%s/%s' % (setting.image_store_path, image_name[:2])
    if not os.path.exists(to_path):
        os.makedirs(to_path)
        os.chmod(to_path, 0777)
    h=open('%s/%s' % (to_path, image_name), 'wb')
    h.write(data)
    h.close()
    return image_name


# 通知放到队列，异步处理
# type: alipay, wxpay, iap
def event_push_notify(notify_type, notify_data, order_trade_id=''):
    if notify_type not in ['alipay','wxpay','iap']:
        return None

    db.event_queue.insert_one({
        'type' : 'PAY_NOTIFY',
        'status' : 'WAIT',
        'data' : {
            'type' : notify_type,
            'data' : notify_data,
            'order_trade_id' : order_trade_id,
        }
    })

    return True

## ---------------- for app use ------------------------------------------------

# 生成随机id
def randomid(realid):
    realid = str(realid)
    newid = db.randomid.insert_one({'real_id' : realid, 'tick' : int(time.time())})
    newid = str(newid.inserted_id)
    #print realid, '---->', newid
    return newid

# 取回真实id
def realid(randid):
    from bson.objectid import ObjectId
    import traceback
    try:
        r = db.randomid.find_one_and_update({'_id' : ObjectId(randid)}, {'$set' : { 'tick' : int(time.time())}})
        if r is None:
            return None
        else:
            print r['real_id'], '<----', randid
            return r['real_id']
    except Exception, e:
        traceback.print_exc()
        return None

# 记录api调用
def log_app_api(version, call_name, param):
    db.log_app_api.insert_one({
        'version' : version,
        'call'    : call_name,
        'param'   : param,
        'source'  : web.ctx.ip,
        'agent'   : web.ctx.environ.get('HTTP_USER_AGENT', ''),
        'tick'    : int(time.time()),
        'time_t'  : time_str(),
    })


# 点击数增一
def click_inc():
    db.sys_refs.update_one(
        {'name' : 'click_count'}, 
        {'$inc' : {'c' : 1}}, 
        upsert=True
    )
