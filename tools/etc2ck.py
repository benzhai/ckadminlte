#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
from __future__ import print_function

import sys
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import threading

import json

import random


path = sys.argv[1]

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


def load_etc_cookie(path):
    FILE = open(path, 'rb')
    fieldlist = json.load(FILE)

    cookie = dict()
    for field in fieldlist:
        fieldname = field['name']
        fieldvalue = field['value']
        cookie[fieldname] = fieldvalue
        print ("%s=%s;" %(fieldname, fieldvalue), end=" ")

    #print cookie
    print ("\n")

    return cookie
    

cookie = load_etc_cookie(path)


#print cookie

