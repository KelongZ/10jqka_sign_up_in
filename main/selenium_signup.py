# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 16:26:53 2019

@author: Kelong
"""
from aip import AipOcr
from PIL import Image, ImageEnhance

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.keys import Keys # 键盘事件

from mysql_handle import DataBaseHandle
import phone

import time
import json
import random
import string
import os
import sys
import multiprocessing
import re

# 从数据库获取登录信息
def get_sign_in_info():
    db = DataBaseHandle('192.168.9.93', 3306, 'dengtacj', 'dengtacj2015', 'db_spider')
    sql = "SELECT tele_number,account,password FROM spider_cookies WHERE status_code = -8"
    # 返回tuple类型值
    info = db.select_sql(sql)
    if info:
        global status_code
        global tele_number
        global password
        status_code = 0
        tele_number = info[0][0]
        account = info[0][1]
        password = info[0][2]
        return account
    else:
        print('已无cookies可以更新,退出程序')
        driver.quit()
        sys.exit(0)

# 对接sign_in函数
def sign_in_cookies_update_to_mysql(account): 
    ''' 获取json格式cookies '''
    cookie_list = driver.get_cookies()
    #print(cookie_list)
    ''' 注意引号替换，否则insert会报错 '''
    cookie_list_ = str(cookie_list)
    cookie_list_ = cookie_list_.replace("'",'"')
    #这里可以不用格式化输出 jsonCookies = json.dumps(cookie_list, sort_keys=True, indent=4, separators=(',', ': '))
    #print(jsonCookies)
    ''' 获取cookies串 '''
    cookie = [item["name"] + "=" + item["value"] for item in cookie_list]
    cookiestr = '; '.join(item for item in cookie)
    #print(cookiestr)

    db = DataBaseHandle('192.168.9.93', 3306, 'dengtacj', 'dengtacj2015', 'db_spider')
    sql = "REPLACE INTO spider_cookies (tele_number,account,password,cookies_js,cookies_str,account_origin,status_code) VALUES ('%s','%s','%s','%s','%s','%s','%s')" % (tele_number,account,password,cookie_list_,cookiestr,account_origin,status_code)
    db.insert_sql(sql)
    #print(result)
    db.close()

# 对接sign_up函数
def sign_up_cookies_handle_to_mysql(account):    
    ''' 获取json格式cookies '''
    cookie_list = driver.get_cookies()
    #print(cookie_list)
    ''' 注意引号替换，否则insert会报错 '''
    cookie_list_ = str(cookie_list)
    cookie_list_ = cookie_list_.replace("'",'"')
    #这里可以不用格式化输出 jsonCookies = json.dumps(cookie_list, sort_keys=True, indent=4, separators=(',', ': '))
    #print(jsonCookies)
    ''' 获取cookies串 '''
    cookie = [item["name"] + "=" + item["value"] for item in cookie_list]
    cookiestr = '; '.join(item for item in cookie)
    #print(cookiestr)

    db = DataBaseHandle('192.168.9.93', 3306, 'dengtacj', 'dengtacj2015', 'db_spider')
    sql = "INSERT INTO spider_cookies (tele_number,account,password,cookies_js,cookies_str,account_origin,status_code) VALUES ('%s','%s','%s','%s','%s','%s','%s')" % (tele_number,account,password,cookie_list_,cookiestr,account_origin,status_code)
    db.insert_sql(sql)
    #print(result)
    db.close()

def show_cookies():
    # 逐条展示cookie
    for cookie in driver.get_cookies():
         print("%s/%s" % (cookie['name'],cookie['value']))

# 格式化输出cookies到本地json文件
def save_cookies():
    # 获取cookies
    cookie = driver.get_cookies()
    # 格式化输出json
    jsonCookies = json.dumps(cookie, sort_keys=True, indent=4, separators=(',', ': '))
    # 输出到文件
    with open(r'..\cookie\thscookie.json', 'w') as f:
        f.write(jsonCookies)

def save_cookies_str():
    # 文本处理jsonCookies成我们需要格式（cookies串）
    with open(r'..\cookie\ths_user3_cookies.json','r',encoding='utf-8') as f:
        listCookies=json.loads(f.read())
    cookie = [item["name"] + "=" + item["value"] for item in listCookies]
    # cookie串注意空格
    cookiestr = '; '.join(item for item in cookie)
    print(cookiestr)
    return cookiestr

# 依次添加cookie到driver中
def read_cookies(cookiesfile):
    ''' Easy_way：listCookies = json.load(open(cookiesfile,'r',encoding='utf-8'))'''
    with open(cookiesfile,'r',encoding='utf-8') as f:
        listCookies = json.loads(f.read())
    for cookie in listCookies:
        driver.add_cookie(cookie)
    driver.refresh() # 读取完cookie刷新页面

# 判断网页元素是否存在
def is_element_exist(css):
    s = driver.find_elements_by_css_selector(css_selector=css)
    if len(s) == 0:
        '''print("元素未找到：%s" % (css))'''
        return False
    elif len(s) == 1:
        return True
    else:
        '''print("找到%s个元素：%s" % (len(s), css))'''
        return False

# 手动定位
def get_ocr_img(): 
    driver.save_screenshot(screen_shot_loc) # 截取屏幕内容，保存到本地
    ran = Image.open(screen_shot_loc) # 打开截图，获取验证码位置，截取保存验证码
    box = (1225, 188, 1301, 222)  # 手动定位
    ran.crop(box).save(ocr_loc)
    return ocr_loc

# 自动定位,参数为验证码css定位
def auto_get_ocr_img(css):
    driver.get_screenshot_as_file(screen_shot_loc)
    location = driver.find_element_by_css_selector(css).location
    size = driver.find_element_by_css_selector(css).size
    left = location['x']
    top =  location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    ran = Image.open(screen_shot_loc)
    ran.crop((left,top,right,bottom)).save(ocr_loc)
    time.sleep(1)
    return ocr_loc

# 获取手机号
def get_phone_num():
    global tele_number
    global key
    key = phone.login()
    phone.getSummary(key)
    
    tele_number = phone.getPhone(sid,key)
    max_try = 0
    ''' 如果第三方无手机号，等待3s直到取到手机号 '''
    while tele_number is None:
        time.sleep(3)
        tele_number = phone.getPhone(sid,key)
        max_try += 1
        if max_try == 20:
            print('平台无手机号，退出程序')
            driver.quit()
            sys.exit(0)

# 获取验证码
def get_verify_code():
    global status_code
    status_code = 0
    
    message = None
    maxcount = 0
    while message is None:
        message = phone.getMessage(sid,tele_number,key)
        maxcount += 1
        time.sleep(3)
        if maxcount == 20:
            phone.addBlacklist(sid,tele_number,key)
            message = '%s手机号已被拉黑' %(tele_number)
            status_code = -90 # 未获取到验证码，手机号已被拉黑
            print(message)
            verify_code = ''
            return verify_code
        
    try:
        verify_code_group = re.search('验证码是(\d+)', message)
        verify_code = verify_code_group.group(1)
        return verify_code
    # ''' 如果message返回1有内容但是无验证码，执行except '''
    except:
        phone.addBlacklist(sid,tele_number,key)
        status_code = -90
        print('手机号已被注册,已拉黑手机号')
        verify_code = ''
        return verify_code

def sign_up():
    driver.get(url_sign_up)
    driver.maximize_window()
    ''' 获取电话号码，获取不到(一般是余额不足)直接退出主程序 '''
    get_phone_num()
    driver.find_element_by_css_selector(".reg-form .phone").send_keys(tele_number)
    time.sleep(0.4)
    '''  自动生成12位长度账户名 '''
    ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    driver.find_element_by_css_selector(".reg-form .account").send_keys(ran_str)
    time.sleep(0.4)
    
    driver.find_element_by_css_selector(".reg-form .passwd1").send_keys(password)
    time.sleep(0.4)
    driver.find_element_by_css_selector(".reg-form .passwd2").send_keys(password)
    time.sleep(0.4)
    
    '''  如果用户名已存在，重新赋值直到用户名不重复（判断条件：属性text值是否存在） '''
    account_flag = driver.find_element_by_css_selector("#phonef > ul > li:nth-child(2) > div > div.yk-validate-bbs > em").text != ''
    print("account_flag: %s" % account_flag)
    while account_flag:
        ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        driver.find_element_by_css_selector(".reg-form .account").clear()
        driver.find_element_by_css_selector(".reg-form .account").send_keys(ran_str)
        driver.find_element_by_css_selector(".reg-form .account").send_keys(Keys.TAB)
        time.sleep(1)
        account_flag = driver.find_element_by_css_selector("#phonef > ul > li:nth-child(2) > div > div.yk-validate-bbs > em").text != ''
                                        
    '''  如果手机格式错误，重新赋值（判断条件：报错属性是否存在） '''
    tele_flag = driver.find_element_by_css_selector("#phonef > ul > li:nth-child(1) > div > div.yk-validate-bbs > em").text != ''
    print("tele_flag: %s" % tele_flag)
    while tele_flag:
        get_phone_num()
        driver.find_element_by_css_selector(".reg-form .phone").clear()
        driver.find_element_by_css_selector(".reg-form .phone").send_keys(tele_number)
        driver.find_element_by_css_selector(".reg-form .phone").send_keys(Keys.TAB)
        time.sleep(1)
        tele_flag = driver.find_element_by_css_selector("#phonef > ul > li:nth-child(1) > div > div.yk-validate-bbs > em").text != ''
    
    auto_get_ocr_img(".reg-form img") # 获取验证码截图到本地 
    ocr_text = ocr_recognition(ocr_loc) # 验证码识别成string
    driver.find_element_by_css_selector(".reg-form .captcha").send_keys(ocr_text)
    driver.find_element_by_css_selector(".reg-form .captcha").send_keys(Keys.TAB)
    time.sleep(1)
    # 定义一个ocr_flag bool值
    ocr_flag = False
    ocr_flag_text = driver.find_element_by_css_selector("#phonef > ul > li:nth-child(6) > div > div.yk-validate-bbs > em").text
    if ocr_flag_text == '请输入验证码' or ocr_flag_text == '验证码错误':
        ocr_flag = True
    else:
        ocr_flag = False
    while ocr_flag:
        '''  ocr识别错误并重试 '''
        auto_get_ocr_img(".reg-form img") # 获取验证码截图到本地 
        ocr_text = ocr_recognition(ocr_loc) # 验证码识别成string
        while ocr_text == '':
            driver.find_element_by_css_selector(".reg-form img").click()
            auto_get_ocr_img(".reg-form img") # 获取验证码截图到本地 
            ocr_text = ocr_recognition(ocr_loc) # 验证码识别成string
            
        driver.find_element_by_css_selector(".reg-form .captcha").clear()
        driver.find_element_by_css_selector(".reg-form .captcha").send_keys(ocr_text)
        driver.find_element_by_css_selector(".reg-form .captcha").send_keys(Keys.TAB)
        time.sleep(1)
        ocr_flag_text = driver.find_element_by_css_selector("#phonef > ul > li:nth-child(6) > div > div.yk-validate-bbs > em").text
        if ocr_flag_text == '':
            ocr_flag = False
        else:
            ocr_flag = True
    time.sleep(1)
    print('OCR识别成功')
    ''' 提交注册 '''
    driver.find_element_by_css_selector(".submit-field .submit").send_keys(Keys.ENTER)
    time.sleep(1)
    
    ''' 判断是否跳转到接收手机验证码页面,如果未跳转，说明IP被封，退出程序 '''
    submit_flag = is_element_exist("#submit_for_MT")
    if not submit_flag:
        driver.quit()
        print('IP挂了，请更换IP或者择日再试')
        sys.exit(0)
    print('提交注册成功')
    
    ''' 验证码识别 '''
    verify_code = get_verify_code()
    driver.find_element_by_css_selector("#verifyCode").send_keys(verify_code)
    time.sleep(1)
    # 提交验证码
    driver.find_element_by_css_selector("#submit_for_MT").send_keys(Keys.ENTER)
    print('注册完成')
    
    ''' 回到同花顺首页 '''
    time.sleep(1)
    driver.get(url_main)
    
    return ran_str

''' 可以用于自动更新cookies,暂时可以不用,如需要用验证码识别代码需要补充 '''
def sign_in(account):
    driver.get(url_sign_in)
    driver.maximize_window()
    driver.find_element_by_css_selector("#username").clear()
    driver.find_element_by_css_selector("#password").clear()
    driver.find_element_by_css_selector("#username").send_keys(account)
    driver.find_element_by_css_selector("#password").send_keys(password)
    time.sleep(1)
    # 检查是否验证码填写框在网页上可见
    if driver.find_element_by_css_selector("#captchaCode").is_displayed():
        # 获取验证码截图到本地
        ocr_loc = auto_get_ocr_img("#captchaImg")
        # 验证码识别成string
        ocr_text = ocr_recognition(ocr_loc)
        driver.find_element_by_css_selector("#captchaCode").send_keys(ocr_text)
        print(ocr_text)  
    driver.find_element_by_css_selector("#loginBtn").click()
    time.sleep(1)
    driver.get(url_main)

def ocr_recognition(pic_url):
    """ 你的 APPID AK SK """
    APP_ID = '17591348'
    API_KEY = '6Vh61XMbjBRcnmbVq4SfqZGg'
    SECRET_KEY = 'XoOsLH0ClL77xXDC0XKqjTS7lhQYTAvD'
    
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    
    # 图片地址
    fname = pic_url
    
    """ 读取图片 """
    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()
    
    image = get_file_content(fname)
    
    """ 调用通用文字识别, 图片参数为本地图片 """
    results = client.basicAccurate(image)["words_result"] # 获取结果
    if results:
        text = (results[0]["words"])
        return text.strip().lower()
    else:
        return ''

def main():
    ''' 给sign_in用的默认变量 '''
    global tele_number
    tele_number = ""
    global status_code
    status_code = 0
    
    ''' 全局固定变量 '''
    global password
    password = "1234567899"
    global account_origin
    account_origin = "10jqka"
    global sid
    sid = '8380'
    
    ''' 网址 '''
    global url_main
    url_main = 'http://www.10jqka.com.cn/' # 首页
    global url_sign_up
    url_sign_up = 'http://upass.10jqka.com.cn/register' # 注册页面
    global url_sign_in
    url_sign_in = 'http://upass.10jqka.com.cn/login?redir=HTTP_REFERER' # 登录页面
    
    ''' 屏幕截图和验证码截图地址 '''
    global screen_shot_loc
    screen_shot_loc = r"C:\Users\Administrator\Desktop\dt-爬虫\pic\screen.png"
    global ocr_loc
    ocr_loc = r"C:\Users\Administrator\Desktop\dt-爬虫\pic\ocr.png"
    
    chrome_opt = Options()      # 创建参数设置对象.
    #chrome_opt.add_argument('--headless')   # 无界面化.
    #chrome_opt.add_argument('--disable-gpu')    # 配合上面的无界面化.
    #chrome_opt.add_argument('--window-size=1366,768')   # 设置窗口大小, 窗口大小会有影响.
    #chrome_opt.add_argument('--user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36')
    chrome_opt.add_argument('--proxy-server=114.55.218.114:2013')
    # 创建Chrome对象并传入设置信息.
    global driver
    driver = webdriver.Chrome(chrome_options=chrome_opt)
    
    print('-----------Start------------')
    
    ''' pattern one '''
    if flag == '1':
        account = sign_up()
        sign_up_cookies_handle_to_mysql(account)
        print('%s账户Cookies已入数据库'%(tele_number))
        
    ''' pattern two '''
    if flag == '2':
        account = get_sign_in_info()
        sign_in(account)
        sign_in_cookies_update_to_mysql(account) 
        print('%s账户Cookies已更新'%(tele_number))
        
    print('-----------finish------------\n')
    time.sleep(1)
    driver.quit()

if __name__ == '__main__':
    ''' 备注：一个ip每天最多注册10个账号 '''
    f = False
    while not f:
        flag = input('注册or登陆or退出?(1/2/0?)：')
        if flag == '1':
            f = True
        elif flag == '2':
            f = True
        elif flag == '0':
            sys.exit(0)
        else:
            print('请输入正确的执行条件')
            f = False
    num = int(input('请输入执行次数：'))
    for i in range(num):
        main()