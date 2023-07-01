# 用于爬取车站代号
import re

import openpyxl
import requests


def get_station():
    url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9270'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    stations = re.findall("([\u4e00-\u9fa5]+)\|([A-Z]+)", resp.text)
    return stations


def save(lists):
    wb = openpyxl.Workbook()
    ws = wb.active
    for item in lists:
        ws.append(item)
    wb.save('车站代码.xlsx')


if __name__ == '__main__':
    lst = get_station()
    save(lst)
