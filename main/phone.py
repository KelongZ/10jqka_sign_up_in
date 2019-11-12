# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 09:02:21 2019

@author: Kelong
"""

import requests
import time

url = 'http://api.kmiyz.com/api/do.php'
sid = '8380'


def login():
    para_loginIn = {
            'action':'loginIn',
            'name':'313974633',
            'password':'a199301266'
            }
    
    res_loginIn = requests.post(url,para_loginIn)
    print('登录状态  %s' %(res_loginIn.text))
    ''' 获取token '''
    key = res_loginIn.text.split('|')[1]
    return key

def getSummary(key):
    para_getSummary = {
            'action':'getSummary',
            'token':key
            }
    res_getSummary = requests.post(url,para_getSummary)
    print('当前用户信息(1|余额|等级|批量取号数|用户类型)：%s' %(res_getSummary.text))

def getPhone(sid,key):
    para_getPhone = {
            'action':'getPhone',
            'sid':sid,
            'token':key}
    res_getPhone = requests.post(url,para_getPhone)
    print('获取手机号  %s' %(res_getPhone.text))
    phone = res_getPhone.text.split('|')[1]
    if res_getPhone.text.split('|')[0] == '1':
        return phone

def getMessage(sid,phone,key):
    para_getMessage = {
            'action':'getMessage',
            'sid':sid,
            'phone':phone,
            'token':key}
    res_getMessage = requests.post(url,para_getMessage)
    print('获取验证短信  %s' %(res_getMessage.text))
    message = res_getMessage.text.split('|')[1]
    if res_getMessage.text.split('|')[0] == '1':
        return message

def addBlacklist(sid,phone,key):
    para_addBlacklist = {
            'action':'addBlacklist',
            'sid':sid,
            'phone':phone,
            'token':key}
    res_addBlacklist = requests.post(url,para_addBlacklist)
    print('拉黑手机号  %s' %(res_addBlacklist.text))
    
def cancelRecv(sid,phone,key):   
    para_cancelRecv = {
            'action':'cancelRecv',
            'sid':sid,
            'phone':phone,
            'token':key}
    res_cancelRecv = requests.post(url,para_cancelRecv)
    print('释放手机号  %s' %(res_cancelRecv.text))
    
def cancelAllRecv(key):
    para_cancelAllRecv = {
            'action':'cancelAllRecv',
            'token':key}
    res_cancelAllRecv = requests.post(url,para_cancelAllRecv)
    print('释放所有手机号  %s' %(res_cancelAllRecv.text))

def main():
    key = login()
    getSummary(key)
    
    tele_number = getPhone(sid,key)
    
    cancelAllRecv(key)
    '''message = None
    maxcount = 0
    while message is None:
        message = getMessage(sid,tele_number,key)
        maxcount += 1
        time.sleep(3)
        print('获取%d次'%(maxcount))
        if maxcount == 60:
            addBlacklist(sid,tele_number,key)
            message = '%s手机号已被拉黑' %(tele_number)
            print(message)
        
    print(tele_number)
    # getMessage(sid,phone,key)
    
    #print(phone)'''
if __name__ == '__main__':
    main()