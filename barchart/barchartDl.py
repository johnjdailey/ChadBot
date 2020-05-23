import os
import csv
import sys
import fnmatch
import shutil
import time
import re
import config as cfg
import numpy as np
import pandas as pd
import mysql.connector as mysql
import sqlalchemy
from datetime import datetime
from dateutil.parser import parse
from selenium import webdriver
from influxdb import InfluxDBClient
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

pathOfFilesDled = r'C:\\Users\\ChadBot\\Downloads\\'
pathToMoveDLStocks = r'C:\Users\\ChadBot\\Desktop\\barchartdata\\Stocks\\'
pathToMoveDLETF = r'C:\Users\\ChadBot\\Desktop\\barchartdata\\ETF\\'
pathToMoveDLIndices= r'C:\Users\\ChadBot\\Desktop\\barchartdata\\Indices\\'

def dlData():
    chrome_options = Options()
    # chrome_options.add_argument("start-minimized")
    driver = webdriver.Chrome(r'C:\chromedriver.exe', options=chrome_options)
    driver.get("https://www.barchart.com/login")
    element = driver.find_element_by_name("email")
    element.send_keys(cfg.login['user'])
    element = driver.find_element_by_name("password")
    element.send_keys(cfg.login['pass'])
    element.send_keys(Keys.RETURN)
    driver.get("https://www.barchart.com/options/unusual-activity/stocks")
    print("stocks")
    driver.find_element_by_xpath("//span[contains(.,'download')]").click()
    time.sleep(5)
    driver.get("https://www.barchart.com/options/unusual-activity/etfs")
    print("etfs")
    driver.find_element_by_xpath("//span[contains(.,'download')]").click()
    time.sleep(5)
    driver.get("https://www.barchart.com/options/unusual-activity/indices")
    print("Indices")
    driver.find_element_by_xpath("//span[contains(.,'download')]").click()
    time.sleep(5)
    driver.quit()

'''
This function has been deprecated
Bot will not sort csv files and save them in folders or upload to git
New functions implemented to clean up data and push to MySQL DB instead
'''
def sortData():
    # Open dir where the data is downloaded
    # search for file with .csv 
    # search for etf, stocks, indices
    for f_name in os.listdir(pathOfFilesDled):
        if fnmatch.fnmatch(f_name, '*-etfs-*-*-*-*-*.csv'):
            try:
                shutil.copy(pathOfFilesDled + f_name, pathToMoveDLETF)
                print("File Moved: " + f_name)
            except IOError:
                print("Could not move files")
                sys.exit()
        if fnmatch.fnmatch(f_name, '*-indices-*-*-*-*-*.csv'):
            try:
                shutil.copy(pathOfFilesDled + f_name, pathToMoveDLIndices)
                print("File Moved: " + f_name)
            except IOError:
                print("Could not move files")
                sys.exit()
        if fnmatch.fnmatch(f_name, '*-stocks-*-*-*-*-*.csv'):
            try:
                shutil.copy(pathOfFilesDled + f_name, pathToMoveDLStocks)
                print("File Moved: " + f_name)
            except IOError:
                print("Could not move files")
                sys.exit()

'''
Function also deprecated after cleaning past data
'''
def cleanData(dataPath):
    df = pd.read_csv(dataPath).replace('"', '', regex=True)
    dateRgx = re.compile('(\d{2}-\d{2}-\d{2})')
    dateList = dateRgx.findall(dataPath)
    dateStr = str(dateList[0])
    dateT = datetime.strftime(parse(dateStr), '%Y-%m-%d')
    df.insert(0, 'Date Inserted', dateT)
    df = df.set_index('Date Inserted')
    df.rename(columns={'Last Trade':'Time'}, inplace=True)
    df['IV'] = df['IV'].astype(str).str.rstrip('%').astype(float)
    df['Exp Date'] = pd.to_datetime(df['Exp Date'])
    df['Exp Date'] = df['Exp Date'].dt.strftime('%Y-%m-%d')
    df['Time'] = pd.to_datetime(df['Time'])
    df['Time'] = df['Time'].dt.strftime('%H:%M')
    df = df[:-1]
    print(df.head)
    df.to_csv(dataPath)


'''
This function is used to clean existing data that was already scraped
No need to use this function again because new data downloaded will be cleaned
and pushed to MySQL DB
'''
def cleanUpExistingData():
    etfPath = r"A:\\git\\ChadBot\\barchart\\ETF\\"
    indicesPath = r"A:\\git\\ChadBot\\barchart\\Indices\\"
    stockPath = r"A:\\git\\ChadBot\\barchart\\Stocks\\"
    for f_name in os.listdir(etfPath):
        if fnmatch.fnmatch(f_name, '*-etfs-*-*-*-*-*.csv'):
            try:
                cleanData(etfPath + f_name)
                print("ETFs Cleaned")
            except ValueError as e:
                print(e)
    for f_name in os.listdir(indicesPath):
        if fnmatch.fnmatch(f_name, '*-indices-*-*-*-*-*.csv'):
            try:
                cleanData(indicesPath + f_name)
                print("Indices Cleaned")
            except ValueError as e:
                print(e)
    for f_name in os.listdir(stockPath):
        if fnmatch.fnmatch(f_name, '*-stocks-*-*-*-*-*.csv'):
            try:
                cleanData(stockPath + f_name)
                print("Stocks Cleaned")
            except ValueError as e:
                print(e)
    
'''
Open the downloaded files 
append them to respective tables on the db 
'''
def POSTtoDB():
    filesPath = r"A:\\git\\ChadBot\\barchart\\unusual-stocks-options-activity-05-22-2020.csv"
    # db = mysql.connect(
    #     host = cfg.dbLogin['host'],
    #     user = cfg.dbLogin['user'],
    #     password = cfg.dbLogin['pass'],
    #     database = 'test'
    # )
    # cursor = db.cursor()
    # cursor.execute("CREATE TABLE users (name VARCHAR(255), user_name VARCHAR(255))")

    df = pd.read_csv(filesPath)
    print(df.head)

    # Connect to time series influxDB 
    client = InfluxDBClient(host=cfg.dbLogin['host'], port=cfg.dbLogin['port'])
    # Get the influd dbs on the server
    print(client.get_list_database())

    




if __name__ == "__main__":
    # dlData()
    # sortData()
    # sys.exit()

    POSTtoDB()
    # cleanUpExistingData()