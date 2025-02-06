import csv
import json
from xmlrpc.client import boolean
import pandas as pd

from datetime import datetime
from typing import Dict, Tuple, Union
from bs4 import BeautifulSoup

import pywencai
import requests


def date_to_xls_num(date=datetime.today().date()) -> int:
    if isinstance(date, str):
        dt1 = datetime.strptime(date, '%Y-%m-%d').date()
        # dt1 = dt1.date()
    else:
        dt1 = date
    return (dt1 - datetime(1900, 1, 1).date()).days + 2


def qingxushuju() -> Tuple[int, int, int, int, int, int]:
    print('开始获取问财情绪数据')

    zhangting = pywencai.get(query='今日涨停，剔除st', loop=True, sleep=3)
    if zhangting is not None:
        zhangtings = zhangting.shape[0]
    else:
        zhangtings = 0
    print(f'涨停数据获取完成，数量: {zhangtings}')

    shouban = pywencai.get(query='今日连板数=1，剔除st', loop=True, sleep=3)
    if shouban is not None:
        shoubans = shouban.shape[0]
    else:
        shoubans = 0
    print(f'首板数据获取完成，数量: {shoubans}')

    zhaban = pywencai.get(query='今日炸板，剔除st', loop=True, sleep=3)
    if zhaban is not None:
        zhabans = zhaban.shape[0]
    else:
        zhabans = 0
    print(f'炸板数据获取完成，数量: {zhabans}')

    dieting = pywencai.get(query='今日跌停板，剔除st', loop=True, sleep=3)
    if dieting is not None:
        dietings = dieting.shape[0]
    else:
        dietings = 0
    print(f'跌停数据获取完成，数量: {dietings}')

    cengdieting = pywencai.get(query='今日曾触及跌停，剔除st', loop=True, sleep=3)
    if cengdieting is not None:
        cengdietings = cengdieting.shape[0]
    else:
        cengdietings = 0
    qiaobans = cengdietings - dietings
    print(f'撬板数据获取完成，数量: {qiaobans}')

    dajine = pywencai.get(query='今日成交额大于15亿', loop=True, sleep=3)
    if dajine is not None:
        dajines = dajine.shape[0]
    else:
        dajines = 0
    print(f'大成交额数据获取完成，数量: {dajines}')

    print('情绪数据获取成功')
    print(f'{zhangtings},{shoubans},{zhabans},{dietings},{qiaobans},{dajines}')

    return zhangtings, shoubans, zhabans, dietings, qiaobans, dajines


def marketRankCalc(rankcode: str) -> str:
    a, b = divmod(int(rankcode), 65537)
    ranks = f'{a + b}天{a}板'
    if a == 1:
        ranks = '首板'
    elif b == 0:
        ranks = f'{a}板'
    return ranks


def getIndexInfo() -> Tuple[float, float]:
    cookies = {
        'Hm_lvt_929f8b362150b1f77b477230541dbbc2': '1730125965,1730204112',
        'Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1': '1730125965,1730204112',
        'Hm_lvt_722143063e4892925903024537075d0d': '1730125965,1730204112,1730604604',
        'Hm_lpvt_722143063e4892925903024537075d0d': '1730604604',
        'HMACCOUNT': '602A2004D21EF9B8',
        'v': 'A4FMTXgDgvZke-7CvdU0u5WZkMaervT5HyWZvePWfOnmSa-4K_4FcK9yqYBw',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        # 'Cookie': 'Hm_lvt_929f8b362150b1f77b477230541dbbc2=1730125965,1730204112; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1730125965,1730204112; Hm_lvt_722143063e4892925903024537075d0d=1730125965,1730204112,1730604604; Hm_lpvt_722143063e4892925903024537075d0d=1730604604; HMACCOUNT=602A2004D21EF9B8; v=A4FMTXgDgvZke-7CvdU0u5WZkMaervT5HyWZvePWfOnmSa-4K_4FcK9yqYBw',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    amount_sh = 0.0
    amount_sz = 0.0
    indexSH: float = 0.0

    response = requests.get(
        'https://q.10jqka.com.cn/zs/detail/code/1A0001/', cookies=cookies, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        board_infos = soup.find('div', class_='board-infos')
        board_infos_sh = {}
        if board_infos:
            for dl in board_infos.find_all('dl'):
                key = dl.find('dt').get_text(strip=True)
                value = dl.find('dd').get_text(strip=True)
                board_infos_sh[key] = value
        amount_sh = float(board_infos_sh['成交额(亿)'])
        indexSH = float(board_infos_sh['指数涨幅'].strip('%'))

    response = requests.get(
        'https://q.10jqka.com.cn/zs/detail/code/399001/', cookies=cookies, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        board_infos = soup.find('div', class_='board-infos')
        board_infos_sz = {}
        if board_infos:
            for dl in board_infos.find_all('dl'):
                key = dl.find('dt').get_text(strip=True)
                value = dl.find('dd').get_text(strip=True)
                board_infos_sz[key] = value
        amount_sz: float = float(board_infos_sz['成交额(亿)'])

    print(f'沪市成交额：{amount_sh} 深市成交额：{
          amount_sz} 两市总和：{amount_sh + amount_sz}')
    return amount_sh + amount_sz, indexSH


class THSData(object):
    def __init__(self):
        self.limit_up_map: Dict[str: str] = {
            '851983': '15天13板',
            '1310744': '24天20板',
            '1572891': '27天24板',
            '1245207': '23天19板',
            '1441818': '26天22板',
            '1507354': '26天23板',
            '1179670': '22天18板',
            '1114133': '21天17板',
            '983060': '20天15板',
            '1048596': '20天14板',
            '1376279': '23天21板',
            '983059': '19天15板',
            '1310742': '22天20板',
            '655371': '13天11板',
            '917522': '18天14板',
            '917520': '16天14板',
            '851984': '16天13板',
            '720909': '11天10板',
            '1245205': '21天19板',
            '983057': '17天15板',
            '851985': '17天13板',
            '917519': '15天14板',
            '655375': '15天10板',
            '917518': '14板',
            '851982': '14天13板',
            '786446': '14天12板',
            '655374': '14天10板',
            '589838': '14天9板',
            '851981': '13板',
            '786445': '13天12板',
            '589837': '13天9板',
            '524301': '13天8板',
            '458765': '13天7板',
            '786444': '12板',
            '655372': '12天10板',
            '589836': '12天9板',
            '524300': '12天8板',
            '458764': '12天7板',
            '393228': '12天6板',
            '720907': '11板',
            '589835': '11天9板',
            '524299': '11天8板',
            '458763': '11天7板',
            '393227': '11天6板',
            '655370': '10板',
            '589834': '10天9板',
            '524298': '10天8板',
            '458762': '10天7板',
            '393226': '10天6板',
            '327690': '10天5板',
            '262154': '10天4板',
            '589833': '9板',
            '524297': '9天8板',
            '458761': '9天7板',
            '393225': '9天6板',
            '327689': '9天5板',
            '524296': '8板',
            '458760': '8天7板',
            '393224': '8天6板',
            '327688': '8天5板',
            '262152': '8天4板',
            '458759': '7板',
            '393223': '7天6板',
            '327687': '7天5板',
            '262151': '7天4板',
            '196615': '7天3板',
            '393222': '6板',
            '327686': '6天5板',
            '262150': '6天4板',
            '196614': '6天3板',
            '327685': '5板',
            '262149': '5天4板',
            '196613': '5天3板',
            '262148': '4板',
            '196612': '4天3板',
            '131076': '4天2板',
            '196611': '3板',
            '131075': '3天2板',
            '131074': '2板',
            '65537': '首板'
        }

        self.title_row_map: Dict[str, int] = {
            '日期': 0,
            '代码': 1,
            '名称': 2,
            '几天几板': 3,
            '涨停类型': 4,
            '原因类别': 5,
            '涨幅': 6,
            '现价': 7,
            '涨停时间': 8,
            '金额': 9,
            '流值': 10,
            '韭研原因': 11  # 同花顺导出数据中该列为连续涨停，后变更为韭研原因
        }

        self.today_xls_num = date_to_xls_num()

        self.limit_up_stock_data: object = None

        return

    @property
    def updown_count(self) -> Tuple[int, int, int]:
        print('get_updown_count 开始运行')
        cookies = {
            'XSRF-TOKEN': 'eyJpdiI6ImY3T1dOTFd4TmJvVEpuWEZJRnJPSVE9PSIsInZhbHVlIjoiMlozaW1OYlU2Znd3Y0xJdkgrZXJzV3lFazZpWjdDWlZaYWxBOXJBbk9aRjdqQm5lSUllZkhhOUNIbXloeHF5Ym1TTlBOc2pIKzVQckxJUEswR3FjeVE9PSIsIm1hYyI6ImQ3M2FkZmM4NjA4Y2E2ZTI1ZjA2ZWI2Y2I5MWY2ZmVjNGZlNDIxYmE4ZDA3ZjQ5ODE2NjgzZjJmNjY4MjdlOWYifQ%3D%3D',
            'laravel_session': 'eyJpdiI6InR2eGQxZXJXc1JuYVNTUzI4aUpwdnc9PSIsInZhbHVlIjoiRmtmcXNld0FQczd5RHMwazlHWUtOaWJ1dkwxRkFsVFNtdmpscmZMcmRvdm9HRUlJQVJIT3lDanlTeUhVdDgrakxWR1Fob1REc01LazdwZ1Y0MmxYU0E9PSIsIm1hYyI6IjJiMWUwNDMwNmIzZTk4MjE4ODgyNzBlMzA0NjcyNDRkODkwNjU2ZTY5NmJjZmQ4MmZlYmMwNzZjYWY4ZDYyMmYifQ%3D%3D',
            'FBouQdkWZwjuryiOQE72LMECsVTcKmSeBbfnz1xx': 'eyJpdiI6IkFKVG5pY2xDTytGajVhSE52d3dpU3c9PSIsInZhbHVlIjoiREpSYUpaamRqSEVyU1dlV2pwNnl0KytnYlBZTm5IYW5nQzVlUnZvMHhzeTJZVGo4STNEWGdLSm1IYWZaZ1FDUXg3c3V0anZHRlJIVlZ3ODZpRnBpYmxcLzJYSzg1MHVXMDJTXC9FXC9RYTNIWGhOM01qTUp0VTMyZDdhMHRFYldDZkVyVWp5WUFUcm9ENlZHVnh1QithdUdcL0lvQXN5a01LNmVlc28rdGNwd095OVdwNnpOc1ZtTFZ4R3dYcFk0bnppUG5YakZKK0NxN2hIM2w3dFN5ck82bDJWM05sQTc3MHZLQTJmcWg2WWhcLzJBMmUrSGZTNzVFZ1h4TWVLbDVcL2xrV0s4Rnk2SU9WN1gyN1dYV1gwUmZORk9pZ1A1NGNSd01ObTR6NGgrY0xvTTI5dTE1Tmh0V0h3V0Y3eEw4ZWVpS2E0VVkrbzNcL25pNWhUVXl4cmo4ZGZTdm8rb3VEVkhWYmFqUWZDcmtLQXJcL1V1bzB3dVoybk1NSlFuVXdKT2UwR2xITlN2VUJXcVZFT0M4QTZqUnE0ZUtxZWpaN2lXMUdDbGJjUlJ5SjhjdTNVVlhEVWRIN3loMEFPV0k0SzZxdVVmXC9scXR0T2x3ckJkWTloSkFDY1BiZjdUR2QrUDBQVEVIRkJJM1hrNWFSeG04OVowdGk5UCtzd2dHWERZSkxTOWNuSURQK2Iyc1wvR0ZybVZOT09qWVYzUT09IiwibWFjIjoiYjhhNzg3MmJiYjU4ZTRiMGFiMDIzZGQxOTMzNGEzZWM3YWVkMzU1ZmQ2YzgzNjMxNmY4NDYxZWEzZWUwZTRmMSJ9',
        }

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            # 'Cookie': 'XSRF-TOKEN=eyJpdiI6ImY3T1dOTFd4TmJvVEpuWEZJRnJPSVE9PSIsInZhbHVlIjoiMlozaW1OYlU2Znd3Y0xJdkgrZXJzV3lFazZpWjdDWlZaYWxBOXJBbk9aRjdqQm5lSUllZkhhOUNIbXloeHF5Ym1TTlBOc2pIKzVQckxJUEswR3FjeVE9PSIsIm1hYyI6ImQ3M2FkZmM4NjA4Y2E2ZTI1ZjA2ZWI2Y2I5MWY2ZmVjNGZlNDIxYmE4ZDA3ZjQ5ODE2NjgzZjJmNjY4MjdlOWYifQ%3D%3D; laravel_session=eyJpdiI6InR2eGQxZXJXc1JuYVNTUzI4aUpwdnc9PSIsInZhbHVlIjoiRmtmcXNld0FQczd5RHMwazlHWUtOaWJ1dkwxRkFsVFNtdmpscmZMcmRvdm9HRUlJQVJIT3lDanlTeUhVdDgrakxWR1Fob1REc01LazdwZ1Y0MmxYU0E9PSIsIm1hYyI6IjJiMWUwNDMwNmIzZTk4MjE4ODgyNzBlMzA0NjcyNDRkODkwNjU2ZTY5NmJjZmQ4MmZlYmMwNzZjYWY4ZDYyMmYifQ%3D%3D; FBouQdkWZwjuryiOQE72LMECsVTcKmSeBbfnz1xx=eyJpdiI6IkFKVG5pY2xDTytGajVhSE52d3dpU3c9PSIsInZhbHVlIjoiREpSYUpaamRqSEVyU1dlV2pwNnl0KytnYlBZTm5IYW5nQzVlUnZvMHhzeTJZVGo4STNEWGdLSm1IYWZaZ1FDUXg3c3V0anZHRlJIVlZ3ODZpRnBpYmxcLzJYSzg1MHVXMDJTXC9FXC9RYTNIWGhOM01qTUp0VTMyZDdhMHRFYldDZkVyVWp5WUFUcm9ENlZHVnh1QithdUdcL0lvQXN5a01LNmVlc28rdGNwd095OVdwNnpOc1ZtTFZ4R3dYcFk0bnppUG5YakZKK0NxN2hIM2w3dFN5ck82bDJWM05sQTc3MHZLQTJmcWg2WWhcLzJBMmUrSGZTNzVFZ1h4TWVLbDVcL2xrV0s4Rnk2SU9WN1gyN1dYV1gwUmZORk9pZ1A1NGNSd01ObTR6NGgrY0xvTTI5dTE1Tmh0V0h3V0Y3eEw4ZWVpS2E0VVkrbzNcL25pNWhUVXl4cmo4ZGZTdm8rb3VEVkhWYmFqUWZDcmtLQXJcL1V1bzB3dVoybk1NSlFuVXdKT2UwR2xITlN2VUJXcVZFT0M4QTZqUnE0ZUtxZWpaN2lXMUdDbGJjUlJ5SjhjdTNVVlhEVWRIN3loMEFPV0k0SzZxdVVmXC9scXR0T2x3ckJkWTloSkFDY1BiZjdUR2QrUDBQVEVIRkJJM1hrNWFSeG04OVowdGk5UCtzd2dHWERZSkxTOWNuSURQK2Iyc1wvR0ZybVZOT09qWVYzUT09IiwibWFjIjoiYjhhNzg3MmJiYjU4ZTRiMGFiMDIzZGQxOTMzNGEzZWM3YWVkMzU1ZmQ2YzgzNjMxNmY4NDYxZWEzZWUwZTRmMSJ9',
            'Pragma': 'no-cache',
            'Referer': 'https://zx.10jqka.com.cn/limithotspot/public/html/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/126.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        response = requests.get(
            f'https://zx.10jqka.com.cn/marketinfo/overview/distribution/v3?date={
                datetime.today().date().strftime('%Y%m%d')}',
            cookies=cookies, headers=headers)
        resource = json.loads(response.text)
        print('同花顺涨跌分布数据已获取')

        if resource['status_msg'] == 'success':
            zd_distribution = resource['result']['distribution']
            if len(zd_distribution) != 63:
                exit('同花顺涨跌分布数据结构有变化')
        else:
            exit('同花顺涨跌分布数据获取错误')
        print(f'上涨:{sum(zd_distribution[:31])} 平盘:{
              zd_distribution[31]} 下跌:{sum(zd_distribution[32:])}\n')

        return sum(zd_distribution[:31]), zd_distribution[31], sum(zd_distribution[32:])

    def editLimitUpDetail(self) -> tuple[int, object]:
        print('正在读取同花顺导出文件')
        with open('Table.xls', newline='') as file:
            csv_dat = csv.reader(file, delimiter='\t')
            ths_dat = [row for row in csv_dat if row]
        file.close()
        dftitles = ['日期', '代码', '名称', '几天几板', '涨停类型', '原因类别', '首次涨停时间',
                    '最终涨停时间', '现价', '金额', '竞价金额', '自由流值', '涨幅', '开盘涨幅', '连续涨停天数', 'tmp']
        limitUpDetail = pd.DataFrame(ths_dat[1:], columns=dftitles)

        print('开始处理涨停详细数据')
        limitUpDetail['日期'] = self.today_xls_num
        limitUpDetail['代码'] = limitUpDetail['代码'].str.replace(
            r'S[ZH]', lambda x: x.group().lower(), regex=True)
        limitUpDetail['代码'] = limitUpDetail['代码'].str.replace(
            r'^(4|8|9)', r'bj\1', regex=True)
        limitUpDetail['名称'] = limitUpDetail['名称'].str.replace(
            ' ', '', regex=True)
        # limitUpDetailDataFrame['几天几板'] = limitUpDetailDataFrame['几天几板'].map(self.limit_up_map)
        limitUpDetail['几天几板'] = limitUpDetail['几天几板'].apply(
            marketRankCalc)
        limitUpDetail['涨停类型'] = limitUpDetail['涨停类型'].str.replace(
            r'[手字板]', '', regex=True)  # 这里的数据还是涨停类型
        limitUpDetail['几天几板'] = limitUpDetail['几天几板'] + \
            limitUpDetail['涨停类型']
        limitUpDetail['涨停类型'] = limitUpDetail['连续涨停天数'].astype(
            int)
        limitUpDetail['涨幅'] = limitUpDetail['涨幅'].str.replace(
            '%', '')
        limitUpDetail['现价'] = limitUpDetail['现价'].astype(
            float)
        limitUpDetail['金额'] = limitUpDetail['金额'].astype(int)
        limitUpDetail['竞价金额'] = limitUpDetail['竞价金额'].astype(
            int)
        limitUpDetail['自由流值'] = limitUpDetail['自由流值'].str.replace(
            '亿', '').astype(float) * 100000000
        limitUpDetail['涨幅'] = limitUpDetail['涨幅'].str.replace(
            '%', '').astype(float) / 100
        limitUpDetail['开盘涨幅'] = limitUpDetail['开盘涨幅'].str.replace(
            '%', '').astype(float) / 100
        limitUpDetail['竞价金额'] = limitUpDetail['竞价金额'].astype(
            int)
        limitUpDetail.drop(
            columns='连续涨停天数', axis='columns', inplace=True)
        limitUpDetail.drop(
            columns='tmp', axis='columns', inplace=True)
        limitUpDetail.sort_values(['涨停类型', '最终涨停时间'], ascending=[
                                           False, True], inplace=True)
        self.limit_up_stock_data = limitUpDetail

        print('同花顺涨停股票数据处理完毕')
        print(limitUpDetail.to_string())
        # tmp_list = limitUpDetailDataFrame.values.tolist() # 将df转换成list用于版本2中
        # print(tmp_list)
        return limitUpDetail.shape[0], limitUpDetail

    def profitLossEffectInfo(self) -> None:
        print('开始获取问财情绪数据')

        countPriceLimmit, nullDataFrame = self.getWencaiData('今日涨停，剔除st', False)
        # 涨停
        countfirstLimmit, nullDataFrame = self.getWencaiData('今日连板数=1，剔除st', False)
        # 首板
        countFailBoard, failBoard = self.getWencaiData('今日炸板，剔除st', True)
        failBoard['最新涨跌幅'] = failBoard['最新涨跌幅'].astype(float)
        meanFailBoard = failBoard['最新涨跌幅'].mean() / 100
        # 炸板
        countDownLimmit, downLimmit = self.getWencaiData('今日跌停板，剔除st', True)
        # 跌停
        countallDayDownLimmit, nullDataFrame = self.getWencaiData(
            '今日的跌停类型是一字跌停，剔除st', False)
        # 一字跌停
        countConDownLimmit, nullDataFrame = self.getWencaiData('今日连续的跌停，剔除st', False)
        # 连续跌停
        countUpDownLimmit, nullDataFrame = self.getWencaiData('今日曾涨停，收盘跌停，剔除st', False)
        # 天地板
        countDownUpLimmit, nullDataFramxcwde = self.getWencaiData('今日曾跌停，收盘涨停，剔除st', False)
        # 地天板
        nullCount, preUpLimmit = self.getWencaiData('昨日涨停，剔除st', True)
        preUpLimmit['最新涨跌幅'] = preUpLimmit['最新涨跌幅'].astype(float)
        meanPreUpLimmit = preUpLimmit['最新涨跌幅'].mean() / 100
        # 昨日涨停表现
        nullCount, preConUpLimmit = self.getWencaiData('昨日连续涨停天数>1，剔除st', True)
        preConUpLimmit['最新涨跌幅'] = preConUpLimmit['最新涨跌幅'].astype(float)
        meanPreConUpLimmit = preConUpLimmit['最新涨跌幅'].mean() / 100
        # 昨日连板表现
        nullCount, preFailBoard = self.getWencaiData('昨日炸板，剔除st', True)
        preFailBoard['最新涨跌幅'] = preFailBoard['最新涨跌幅'].astype(float)
        meanPreFailBoard = preFailBoard['最新涨跌幅'].mean() / 100
        # 昨日炸板表现

        print('情绪数据获取成功')
        print(f'涨停数{countPriceLimmit}首板数{countfirstLimmit}炸板数{countFailBoard}'
              f'跌停数{countDownLimmit}连续跌停数{countallDayDownLimmit}'
              f'一字跌停数{countConDownLimmit}天地板数{countUpDownLimmit}地天板数{countDownUpLimmit}'
              f'昨日涨停{meanPreUpLimmit}昨日连板{meanPreConUpLimmit}昨日炸板{meanPreFailBoard}')

    def getWencaiData(self, req: str, detail: bool) -> Tuple[int, pd.DataFrame]:
        reqData = pywencai.get(query=f'{req}', loop=True)
        countReqData = 0
        if reqData is not None and isinstance(reqData, pd.DataFrame):
            countReqData = reqData.shape[0]
        else:
            reqData = pd.DataFrame()
        print(f'{req}数据获取完成，数量: {countReqData}')
        if detail is True:
            return countReqData, reqData
        else:
            return countReqData, pd.DataFrame()

    # def match_after_act(self):
    #     print('正在读取同花顺隔日文件')
    #     with open('af.xls', newline='') as file:
    #         csv_dat = csv.reader(file, delimiter='\t')
    #         af = [row for row in csv_dat if row]
    #     file.close()
    #
    #     yst_data = self.limit_up_stock_data
    #     after_data = pd.DataFrame(af[1:], columns=['代码', '名称', '开盘涨幅', '竞价金额', '涨幅', '金额', 'tmp'])
    #     after_data.drop('代码', axis=1, inplace=True)
    #     after_data.drop('tmp', axis=1, inplace=True)
    #     after_data['开盘涨幅'] = after_data['开盘涨幅'].str.replace('%', '').astype(float) / 100
    #     after_data['竞价金额'] = after_data['竞价金额'].astype(int)
    #     after_data['涨幅'] = after_data['涨幅'].str.replace('%', '').astype(float) / 100
    #     after_data['金额'] = after_data['金额'].astype(int)
    #     print(after_data)
    #
    #     fin_df = pd.merge(yst_data, after_data, on='名称', how='left')
    #     print(fin_df)
    #     return 0


if __name__ != '__main__':
    pass
else:
    a = THSData()
    a.profitLossEffectInfo()