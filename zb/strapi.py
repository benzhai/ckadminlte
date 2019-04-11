#!/usr/bin/python
#-*- coding: UTF-8 -*-
# FileName : strapi.py
# Author   : Shan
# DateTime : 2019/1/9
# SoftWare : PyCharm
from flask import Blueprint, abort,Flask, request, jsonify, render_template, redirect,url_for, send_file, send_from_directory
import os,json
from werkzeug.utils import secure_filename
import chardet
import time,datetime
import base64,sys
import globalvar as gl
import libdb as libdb
import libredis as libredis
import libcommon as libcommon

global logger
global CONF

strapi_bp = Blueprint('strapi', __name__, template_folder='templates/html')

def str_to_timestamp(str):
    timeArray = time.strptime(str, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    return timeStamp

def do_queryOneByDate():
    """
    :return:
    """
    # 测试命令：curl -d "action=queryOneByDate&day=2019-1-7" -X POST http://localhost:8889/strapi/http.do
    ou = dict(error=0, data=dict(), msg='ok')
    day = request.form.get('day')
    if day == None:
        ou['error'] = 3
        ou['msg'] = '参数错误'
        return ou
    timestampBegin = str_to_timestamp(day + ' 0:0:0')
    timestampEnd = str_to_timestamp(day + ' 23:59:59')
    conditon = 'lastdate >= %d and lastdate <= %d and update_fail <= 5' % (timestampBegin, timestampEnd)
    sql = libdb.LibDB().query_one_by_condition(conditon, CONF['database']['table'])
    if sql == False:
        ou['error'] = 4
        ou['msg'] = '读账号信息从数据库失败'
        return ou
    count = libdb.LibDB().query_count_by_condition(conditon, CONF['database']['table'])
    if count == False:
        ou['error'] = 4
        ou['msg'] = '读账号数量从数据库失败'
        return ou
    total = count[0]

    if total == 0:
        data_str = '%d|none' % (total)
    else:
        data_str = '%d|%s|%s|%s' % (total, sql[2], sql[3], sql[9])
    logger.debug('账号信息：%s', data_str)
    data_encryed = base64.b64encode(data_str)
    ou['msg'] = '获取成功'
    ou['data']['acc'] = data_encryed
    return ou

def do_queryOneOutDate():
    ou = dict(error=0, data=dict(), msg='ok')
    # 测试命令：curl -d "action=queryOneOutDate" -X POST http://localhost:8200/strapi/http.do
    timestamp = int(time.time() - 3600 * 24 * 6)
    coldtimestamp = int(time.time())
    conditon = 'lastdate <= %d and colddate <= %d and update_fail <= 5' % (timestamp, coldtimestamp)
    sql = libdb.LibDB().query_one_by_condition(conditon, CONF['database']['table'])
    if sql == False:
        ou['error'] = 4
        ou['msg'] = '读账号信息从数据库失败'
        return ou
    count = libdb.LibDB().query_count_by_condition(conditon, CONF['database']['table'])
    if count == False:
        ou['error'] = 4
        ou['msg'] = '读账号数量从数据库失败'
        return ou
    total = count[0]
    if total == 0:
        data_str = '%d|none' % (total)
    else:
        data_str = '%d|%s|%s|%s' % (total, sql[2], sql[3], sql[9])
        # 冷却表项，5分钟
        rv = libcommon.updateColdDateToDB(sql[2], coldtimestamp + 300)
        if rv != True:
            ou['error'] = 4
            ou['msg'] = '冷却表项失败'
            return ou
    # logger.debug('account info：%s',data_str)
    data_encryed = base64.b64encode(data_str)
    ou['msg'] = '获取成功'
    ou['data']['acc'] = data_encryed
    return ou

def do_queryOne():
    ou = dict(error=0, data=dict(), msg='ok')
    # 测试命令：curl -d "action=queryOne" -X POST http://localhost:8889/strapi/http.do
    timestamp = int(time.time() - 3600 * 24 * 6)
    conditon = 'lastdate >= %d and update_fail <= 5' % (timestamp)
    sql = libdb.LibDB().query_one_by_condition(conditon, CONF['database']['table'])
    if sql == False:
        ou['error'] = 4
        ou['msg'] = '读账号信息从数据库失败'
        return ou
    count = libdb.LibDB().query_count_by_condition(conditon, CONF['database']['table'])
    if count == False:
        ou['error'] = 4
        ou['msg'] = '读账号数量从数据库失败'
        return ou
    total = count[0]
    if total == 0:
        data_str = '%d|none' % (total)
    else:
        data_str = '%d|%s|%s|%s' % (total, sql[2], sql[3], sql[9])
    logger.debug('账号信息：%s', data_str)
    data_encryed = base64.b64encode(data_str)
    ou['msg'] = '获取成功'
    ou['data']['acc'] = data_encryed
    return ou

def do_queryOneByIndex(index):
    """
    按照索引从数据库获取账号
    :param index: 从0开始，和表项的id不是一个数值
    :return:
    """
    ou = dict(error=0, data=dict(), msg='ok')
    # 测试命令：curl -d "action=queryOneByIndex&index=0" -X POST http://localhost:8200/strapi/http.do
    key = 'id'
    info = libdb.LibDB().min_key(key, CONF['database']['table'])
    if info != False:
        min = info[0]
    else:
        ou['error'] = 4
        ou['msg'] = '读取数据库获取索引值最小失败'
        return ou

    info = libdb.LibDB().max_key(key, CONF['database']['table'])
    if info != False:
        max = info[0]
    else:
        ou['error'] = 4
        ou['msg'] = '读取数据库获取索引值最大失败'
        return ou

    count = libdb.LibDB().query_count(CONF['database']['table'])
    if count != False:
        Digit = int(count[0])
    else:
        ou['error'] = 4
        ou['msg'] = '读取数据库表现数量失败'
        return ou

    if index >= Digit:
        ou['error'] = 4
        ou['msg'] = '索引值溢出'
        return ou

    conditon = 'select id from %s order by id asc  limit %d' %(CONF['database']['table'], index+1)
    sql = libdb.LibDB().query_all_by_condition(conditon)
    if sql == False:
        ou['error'] = 4
        ou['msg'] = '读账号信息从数据库失败'
        return ou
    logger.info(sql)
    sql_id = sql[-1][0]
    logger.info('sql_id: %s', sql_id)

    sql = libdb.LibDB().query_one('id', sql_id, CONF['database']['table'])
    if sql == False:
        ou['error'] = 4
        ou['msg'] = '读账号信息从数据库失败'
        return ou

    data_str = '1|%s|%s|%s' % (sql[2], sql[3], sql[9])
    logger.debug('账号信息：%s', data_str)
    data_encryed = base64.b64encode(data_str)
    ou['msg'] = '获取成功'
    ou['data']['acc'] = data_encryed
    return ou

def do_insertOne():
    ou = dict(error=0, data=dict(), msg='ok')
    # 测试命令：curl -d "action=insertOne&entry=xxxx" -X POST http://localhost:8889/strapi/http.do
    entry = request.form.get('entry')
    if entry == None:
        ou['error'] = 3
        ou['msg'] = '参数错误'
        return ou
    logger.debug('before decrypt: ' + entry)
    str = base64.b64decode(entry)
    logger.debug('after decrypt: ' + str)
    str = str.split('|')
    logger.debug(str)
    rv = libcommon.cookieWriteToDB(str[0], str[1], str[2])
    if rv != True:
        ou['error'] = 1
        ou['msg'] = '写数据库失败'
        return ou
    ou['data']['num'] = 1
    ou['msg'] = 'insert success'
    return ou

def do_queryOneByNickname():
    ou = dict(error=0, data=dict(), msg='ok')
    # 测试命令：curl -d "action=queryOneByNickname&nick=xxxx" -X POST http://localhost:8889/strapi/http.do
    nick = request.form.get('nick')
    if nick == None:
        ou['error'] = 3
        ou['msg'] = '参数错误'
        return ou
    sql = libdb.LibDB().query_one('nickname', nick, CONF['database']['table'])
    if sql == False:
        ou['error'] = 4
        ou['msg'] = '读数据库失败'
        return ou
    if sql == None:
        ou['msg'] = '没有该用户信息'
        t = dict()
        t['id'] = None
        t['uid'] = None
        t['nickname'] = None
        t['password'] = None
        t['regdate'] = None
        t['lastdate'] = None
        t['colddate'] = None
        t['lastip'] = None
        t['usednum'] = None
        t['cookie'] = None
    else:
        ou['msg'] = 'read success'
        t = dict()
        t['id'] = sql[0]
        t['uid'] = sql[1]
        t['nickname'] = sql[2]
        t['password'] = sql[3]
        t['regdate'] = datetime.datetime.fromtimestamp(sql[4])
        t['lastdate'] = datetime.datetime.fromtimestamp(sql[5])
        t['colddate'] = datetime.datetime.fromtimestamp(sql[6])
        t['lastip'] = sql[7]
        t['usednum'] = sql[8]
        t['cookie'] = sql[9]
    ou['data'] = t
    return ou

def do_updateOne():
    ou = dict(error=0, data=dict(), msg='ok')
    # 测试命令：curl -d "action=updateOne&entry=xxxx" -X POST http://localhost:8889/strapi/http.do
    entry = request.form.get('entry')
    if entry == None:
        ou['error'] = 3
        ou['msg'] = '参数错误'
        return ou
    logger.debug('获取加密前：' + entry)
    str = base64.b64decode(entry)
    logger.debug('解密后：' + str)
    str = str.split('|')
    logger.debug(str)
    if len(str) == 3:
        rv = libcommon.cookieUpdateToDB(str[0], str[1], str[2])
    elif len(str) == 2:
        rv = libcommon.updateFailWriteToDB(str[0], str[1])
    if rv != True:
        ou['error'] = 1
        ou['msg'] = 'updaet DB failed'
        return ou
    ou['data']['num'] = 1
    ou['msg'] = 'update success'
    return ou

def http_do_action(action):
    """
    :param action:
    :return:   ou  ：字典，包含信息
               ou['data']['xxx']        :
               ou['msg']                :信息
               ou['error']              : 0 ok
                                        : 1 写数据库失败
                                        : 2 命令字暂不支持
                                        : 3 参数错误
                                        : 4 读数据库失败
    """
    ou = dict(error=0, data=dict(), msg='ok')
    if action == 'queryOneByDate':
        ou = do_queryOneByDate()
    elif action == 'queryOneOutDate':
        ou = do_queryOneOutDate()
    elif action == 'queryOne':
        ou = do_queryOne()
    elif action == 'queryOneByIndex':
        index = request.form.get('index')
        if index == None:
            ou['error'] = 3
            ou['msg'] = '参数错误'
            return ou
        index = int(index)
        ou = do_queryOneByIndex(index)
    elif action == 'insertOne':
        ou = do_insertOne()
    elif action == 'queryOneByNickname':
        ou = do_queryOneByNickname()
    elif action == 'updateOne':
        ou = do_updateOne()
    else:
        ou['error'] = 2
        ou['msg'] = '命令字暂不支持'
    return ou

@strapi_bp.route('/http.do',methods=['POST','GET'])
def http_do():
    """
    api 接口
    """
    if request.method != 'POST':
        return 'hello'
    action = request.form.get('action')
    logger.debug('action: %s', action)
    ou = http_do_action(action)
    return jsonify(ou)

logger = gl.get_logger()
CONF   = gl.get_conf()
reload(sys)
sys.setdefaultencoding('utf-8')