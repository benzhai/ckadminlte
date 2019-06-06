#!/usr/bin/python
#-*- coding: UTF-8 -*-
# FileName : libdouyu.py
# Author   : Ben
# DateTime : 2019/5/27
# SoftWare : SlickEdit

import os
import requests
import json

#http://open.douyucdn.cn/api/RoomApi/room/110
import globalvar as gl
global logger
global CONF

def getRoomInfo(room_id):
    url = "http://open.douyucdn.cn/api/RoomApi/room/%s" %(room_id)
    try:
        reply = requests.get(url)
    except:
        return None

    logger.debug("url=%s, reply.status_code=%s" %(url, reply.status_code))


    if reply.status_code == 404:
        return None

    rjson = reply.json()

    '''
    [
        {
            u'data': 
                {
                    u'owner_name': u'\u8c22\u5f6cDD', 
                    u'owner_weight': u'0', 
                    u'cate_name': u'\u5200\u5854\u81ea\u8d70\u68cb', 
                    u'start_time': u'2019-05-27 13:01:08', 
                    u'room_name': u'\u5976\u54e5\u54e5\u306e\u76f4\u64ad\u95f4', 
                    u'room_status': u'1',
                    u'cate_id': u'650', 
                    u'avatar': u'https://apic.douyucdn.cn/upload/avanew/face/201804/06f34dadc391956ce43e714464a91671_big.jpg', 
                    u'room_thumb': u'https://rpic.douyucdn.cn/asrpic/190527/110_1824.png/dy1', 
                    u'online': 367522, 
                    u'hn': 367522, 
                    u'room_id': u'110', 
                    u'fans_num': u'0'
                }, 
            u'error': 0
    }
    '''

    rdata = rjson['data']

    status = dict()
    status['owner_name'] = rdata['owner_name']
    status['owner_weight'] = rdata['owner_weight']
    status['start_time'] = rdata['start_time']
    status['room_name'] = rdata['room_name']
    status['room_status'] = rdata['room_status']
    status['cate_id'] = rdata['cate_id']
    status['cate_name'] = rdata['cate_name']
    status['avatar'] = rdata['avatar']
    status['cate_id'] = rdata['cate_id']
    status['room_thumb'] = rdata['room_thumb']
    status['online'] = rdata['online']
    status['hn'] = rdata['hn']
    status['room_id'] = rdata['room_id']
    status['fans_num'] = rdata['fans_num']

    return status
   

def roomIsOline(room_id):
    status = getRoomStatus(room_id)

logger = gl.get_logger()
CONF   = gl.get_conf()

if __name__ == '__main__':
    status = getRoomStatus("110")
    for key,val in status.items():
        print "%16s: %-s" %(key, val)



