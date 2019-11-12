# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 16:26:53 2019

@author: Kelong
"""

import  pymysql

class DataBaseHandle:
    def __init__(self, ip, port, user, passwd, db_name):
        self.con = pymysql.connect(
            host=ip, port=port, user=user, passwd=passwd, db=db_name, charset='utf8')
        self.cursor = self.con.cursor()

    # 执行查询SQL
    def select_sql(self, sql):
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
#         row = self.cursor.fetchone()
        return result

    # 执行插入SQL
    def insert_sql(self, sql):
        self.cursor.execute(sql)
        self.con.commit()

    # 执行更新SQL
    def update_sql(self, sql):
        self.cursor.execute(sql)
        self.con.commit()
        
    # 执行更新SQL
    def replace_sql(self, sql):
        self.cursor.execute(sql)
        self.con.commit()

    # 执行关闭连接
    def close(self):
        self.cursor.close()
        self.con.close()