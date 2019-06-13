#!/usr/bin/env python
# -*- coding:utf-8 -*-
#Filename:ck2etc.py

import sys
import json

def cookie_parse(line):
    
    fields = line.split(';')

    #print 'fields: ', fields

    cookie = {}
    for field in fields:
        pair = field.split('=')
        key = pair[0].strip()
        val = pair[1].strip()
        cookie[key] = val

    return cookie

def load_cookies(path):
    cookies = []

    FILE = open(path, 'rb')

    for line in FILE:
        line = line.strip('\n')
        if len(line) < 10:
            continue

        cookie = cookie_parse(line)
        cookies.append(cookie)

    return cookies

def ck_to_etc(cookie):
    id = 0
    fieldlist = []
    for key,val in cookie.items():
        field =  {"domain": ".qq.com", \
                     "expirationDate": 2147483645.489204, \
                     "hostOnly": False, \
                     "httpOnly": False, \
                     "name": key, \
                     "path": "/", \
                     "sameSite": "no_restriction", \
                     "secure": False, \
                     "session": False, \
                     "storeId": "0", \
                     "value": val, \
                     "id": id }

        fieldlist.append(field)

        id += 1

    return fieldlist

''''
def etc_dump(etc):
    print "["
    for field in etc:
        print "{"
        for  key,val in field.items():
            print "    \"%s\":%s" %(key, val)
        print "},"

    print "]"
'''

if __name__ == '__main__':

    cookies = load_cookies(sys.argv[1])

    for cookie in cookies:
        etc = ck_to_etc(cookie)
        #etc_dump(etc)
        fmtect = json.dumps(etc, sort_keys=True, indent=4, separators=(',', ':'))
        print fmtect
