#!/usr/bin/env python 3
#coding:utf-8
#vc 上报错：E101：Module 'lxml.etree' has no 'HTML' member(XX,XX) ,但是在python3.5中是可以运行的。

import re
import time
import random
import pymysql

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from lxml import etree

#链接数据库（数据库lagou和数据表company、job是在之前已经建好了）
def dbconnect(): 
    try:
        db = pymysql.connect("localhost", "root", "123456", "lagou",use_unicode=True, charset="utf8")
    except Exception as error:
        print("CONNECTION WRONG:",error)
    return db

#定义一个插入到数据库的函数
def insert(x_zip,table):    
    for m in x_zip:
        sql = '''INSERT INTO {} values {}'''.format(table,m)
        try:
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
        except Exception as error:
            db.rollback()
            print(error)

#定义一个分隔函数
def spt(temp):
    list1,list2 = [],[]
    for i in temp:
        if i.strip():
            list1.append(i.split('/')[0].strip())
            list2.append(i.split('/')[1].strip())
    return list1,list2

#定义爬虫函数
def spider(city):
    url = "https://www.lagou.com/jobs/list_数据分析师?px=default&city={}#filterBox".format(city)
    driver.get(url)
    time.sleep(3)
    #count = 1
    while True:
        s = BeautifulSoup(driver.page_source,'lxml')
        labels=[]
        treatment=[]
        for i in s.findAll('div','list_item_bot'):
            labels.append(i.text.split('“')[0].strip().replace('\n',','))
            treatment.append(i.text.split('“')[1].strip().replace('”',''))
    
        selector=etree.HTML(driver.page_source)

        company_link=selector.xpath('//div[@class="company_name"]/a/@href')
        company_name=selector.xpath('//div[@class="company_name"]/a/text()')
        job_name =selector.xpath('//a[@class="position_link"]/h3/text()')
        job_link = selector.xpath('//a[@class="position_link"]/@href')
        address =selector.xpath('//span[@class="add"]/em/text()')
        temp_1 =selector.xpath('//div[@class="p_bot"]/div[@class="li_b_l"]/text()')
        salary = selector.xpath('//span[@class="money"]/text()')
        temp_2 = selector.xpath('//div[@class="industry"]/text()')
    
        experience,education = spt(temp_1)
        industry,scale = spt(temp_2)
    
        companyID = list(map(lambda x:re.findall(r'\d+',x)[0],company_link))
        jobID = list(map(lambda x:re.findall(r'\d+',x)[0],job_link))
        
        #将数据插入到数据库中
        companys = zip(companyID,company_name,company_link,industry,scale)
        insert(companys,"company")
        jobs = zip(jobID,job_name,address,experience,salary,treatment,job_link,companyID,education,labels,city)
        insert(jobs,"job")
    
        #print(count,s.findAll('span','pager_next pager_next_disabled'))
        if s.findAll('span','pager_next pager_next_disabled'):
            break
        else:
            submitBtn = driver.find_element_by_class_name("pager_next")
            driver.execute_script("arguments[0].scrollIntoView()", submitBtn)
            submitBtn.click()
            time.sleep(random.randint(3,20))
        
        #主要用于检测是否抓取到了‘pager_next pager_next_disabled’元素
        '''count += 1   
        if count == 31:
            print("its all")
            break'''


#设置无头的chrome浏览器参数
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

#运行浏览器
driver = webdriver.Chrome(chrome_options=chrome_options)

#链接数据库
db = dbconnect()

#开始爬虫
city_list = ['北京', '上海','深圳','广州','杭州','成都','南京','武汉','西安','厦门','长沙','苏州','天津','重庆']
for city in city_list:
    spider(city)

#关闭数据库
db.close()