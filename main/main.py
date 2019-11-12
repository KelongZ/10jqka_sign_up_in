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
import sys
import re

''' 操作性函数 '''
# 从数据库获取登录信息
def get_sign_in_info():
    db = DataBaseHandle('192.168.9.93', 3306, 'dengtacj', 'dengtacj2015', 'db_spider')
    sql = "SELECT tele_number,account,password,account_origin FROM spider_cookies WHERE status_code = -8"
    # 返回tuple类型值
    info = db.select_sql(sql)
    if info:
        global status_code
        global tele_number
        global account
        global password
        global account_origin
        status_code = 0
        tele_number = info[0][0]
        account = info[0][1]
        password = info[0][2]
        account_origin = info[0][3]
    else:
        print('已无cookies可以更新,退出程序')
        driver.quit()
        sys.exit(0)

# 对接sign_in函数
def sign_in_cookies_update_to_mysql(): 
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
    sql = "UPDATE spider_cookies SET cookies_js='%s',cookies_str='%s',status_code='%s' WHERE account='%s' AND account_origin='%s';" % (cookie_list_,cookiestr,status_code,account,account_origin)
    db.insert_sql(sql)
    #print(result)
    db.close()
    
    
''' 功能性函数 '''
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

''' 登录 '''
# 同花顺
def sign_in():
    driver.get('http://upass.10jqka.com.cn/login?redir=HTTP_REFERER')
    driver.maximize_window()
    driver.find_element_by_css_selector("#username").clear()
    driver.find_element_by_css_selector("#password").clear()
    driver.find_element_by_css_selector("#username").send_keys(account)
    driver.find_element_by_css_selector("#password").send_keys(password)
    time.sleep(1)
    # 检查是否验证码填写框在网页上可见
    if driver.find_element_by_css_selector("#captchaCode").is_displayed():
        # TODO ''' 只验证了一次，暂时未写验证码错误重写操作 '''
        # 获取验证码截图到本地
        ocr_loc = auto_get_ocr_img("#captchaImg")
        # 验证码识别成string
        ocr_text = ocr_recognition(ocr_loc)
        driver.find_element_by_css_selector("#captchaCode").send_keys(ocr_text)
        print(ocr_text)  
    driver.find_element_by_css_selector("#loginBtn").click()
    time.sleep(1)
    driver.get('http://www.10jqka.com.cn/')

def tou_tiao_sign_in():
    driver.get('https://www.zhihu.com/')
    driver.maximize_window()
    driver.find_element_by_css_selector("div.SignFlow-tabs > div:nth-child(2)").click()
    
    driver.find_element_by_css_selector(".SignFlow-account .Input").clear()
    driver.find_element_by_css_selector(".SignFlow-password .Input").clear()
    driver.find_element_by_css_selector(".SignFlow-account .Input").send_keys('13995647733')
    driver.find_element_by_css_selector(".SignFlow-password .Input").send_keys('a199301266')
    
    time.sleep(10)
    
    driver.find_element_by_css_selector("div.Card.SignContainer-content > div > form > button").click()
    
    time.sleep(5)
    
    pass


def main():
    ''' 屏幕截图和验证码截图地址 '''
    global screen_shot_loc
    screen_shot_loc = r"C:\Users\Administrator\Desktop\dt-爬虫\pic\screen.png"
    global ocr_loc
    ocr_loc = r"C:\Users\Administrator\Desktop\dt-爬虫\pic\ocr.png"
    
    chrome_opt = Options()      # 创建参数设置对象.
    #chrome_opt.add_argument('--headless')   # 无界面化.
    #chrome_opt.add_argument('--disable-gpu')    # 配合上面的无界面化.
    #chrome_opt.add_argument('--window-size=1366,768')   # 设置窗口大小, 窗口大小会有影响.
    chrome_opt.add_argument('--user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36')
    #chrome_opt.add_argument('--proxy-server=114.55.218.114:2013')
    # 创建Chrome对象并传入设置信息.
    global driver
    driver = webdriver.Chrome(chrome_options=chrome_opt)
    
    print('-----------Start------------')
    ''' 同花顺 '''
    if flag == '1':
        get_sign_in_info()
        sign_in()
        sign_in_cookies_update_to_mysql()
        print('%s账户Cookies已更新'%(tele_number))
    if flag == '2':
        #get_sign_in_info()
        tou_tiao_sign_in()
        #sign_in_cookies_update_to_mysql()
        #print('%s账户Cookies已更新'%(tele_number))
    print('-----------finish------------\n')
    time.sleep(1)
    driver.quit()

if __name__ == '__main__':
    flag = '2'
    main()