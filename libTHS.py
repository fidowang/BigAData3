import csv
import json
import pandas as pd

from datetime import datetime
from typing import Dict, Tuple
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


def marketRankCalc(rankcode: str) -> str:
    a, b = divmod(int(rankcode), 65537)
    ranks = f'{a + b}天{a}板'
    if a == 1:
        ranks = '首板'
    elif b == 0:
        ranks = f'{a}板'
    return ranks


def getIndexInfo() -> list:
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
        indexSH = float(board_infos_sh['指数涨幅'].strip('%')) / 100

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

    print(f'沪市成交额：{amount_sh} 深市成交额：{amount_sz} 两市总和：{amount_sh + amount_sz}\n')
    return [amount_sh + amount_sz, indexSH]


class THSData(object):
    def __init__(self):

        self.today_xls_num = date_to_xls_num()

        self.uplimit: object = None
        self.countUpLimit: int = 0

        return

    @property
    def updown_count(self) -> list:
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
        print(f'上涨:{sum(zd_distribution[:31])} 平盘:{zd_distribution[31]} 下跌:{sum(zd_distribution[32:])}\n')

        return [sum(zd_distribution[:31]), zd_distribution[31], sum(zd_distribution[32:])]

    def editLimitUpDetail(self) -> tuple[int, pd.DataFrame]:
        print('正在读取同花顺导出文件')
        with open('Table.xls', newline='') as file:
            csv_dat = csv.reader(file, delimiter='\t')
            ths_dat = [row for row in csv_dat if row]
        file.close()
        dftitles = ['日期', '代码', '名称', '几天几板', '涨停类型', '所属概念', '首次涨停时间', '最终涨停时间', '现价', '金额', '竞价金额', '自由流值', '涨幅',
                    '开盘涨幅', '连续涨停天数', '涨停原因类别', 'tmp']
        limitUpDetail = pd.DataFrame(ths_dat[1:], columns=dftitles)
        if (limitUpDetail['几天几板'] == '--').any() or (limitUpDetail['涨停类型'] == '--').any() or (limitUpDetail['涨停原因类别'] == '--').any():
            exit('几天几板、涨停类型存在“--”，请重新导出数据')

        print('开始处理涨停详细数据')
        limitUpDetail["日期"] = self.today_xls_num
        limitUpDetail["代码"] = limitUpDetail["代码"].str.replace(r"S[ZH]", lambda x: x.group().lower(), regex=True)
        limitUpDetail["代码"] = limitUpDetail["代码"].str.replace(r"^(4|8|9)", r"bj\1", regex=True)
        limitUpDetail["名称"] = limitUpDetail["名称"].str.replace(" ", "", regex=True)
        limitUpDetail["几天几板"] = limitUpDetail["几天几板"].apply(marketRankCalc)
        limitUpDetail["涨停类型"] = limitUpDetail["涨停类型"].str.replace(r"[手字板]", "", regex=True)  # 这里的数据还是涨停类型
        limitUpDetail['几天几板'] = limitUpDetail['几天几板'] + limitUpDetail['涨停类型']
        limitUpDetail['涨停类型'] = limitUpDetail['连续涨停天数'].astype(int)
        limitUpDetail['所属概念'] = limitUpDetail['所属概念'].str.replace('【', '')
        limitUpDetail['所属概念'] = limitUpDetail['所属概念'].str.replace('】', '')
        limitUpDetail['所属概念'] = limitUpDetail['所属概念'].str.replace(';', '+')
        limitUpDetail['涨幅'] = limitUpDetail['涨幅'].str.replace('%', '')
        limitUpDetail['现价'] = limitUpDetail['现价'].astype(float)
        limitUpDetail['金额'] = limitUpDetail['金额'].astype(int)
        limitUpDetail['竞价金额'] = limitUpDetail['竞价金额'].astype(int)
        limitUpDetail['自由流值'] = limitUpDetail['自由流值'].str.replace('亿', '').astype(float) * 100000000
        limitUpDetail['涨幅'] = limitUpDetail['涨幅'].str.replace('%', '').astype(float) / 100
        limitUpDetail['开盘涨幅'] = limitUpDetail['开盘涨幅'].str.replace('%', '').astype(float) / 100
        limitUpDetail['竞价金额'] = limitUpDetail['竞价金额'].astype(int)
        limitUpDetail.drop(columns=['连续涨停天数', 'tmp'], axis='columns', inplace=True)
        limitUpDetail.rename(columns={'涨停类型': '连续涨停天数'}, inplace=True)
        limitUpDetail.sort_values(['连续涨停天数', '最终涨停时间'], ascending=[False, True], inplace=True)
        self.uplimit = limitUpDetail
        self.countUpLimit = limitUpDetail.shape[0]

        print('同花顺涨停股票数据处理完毕')
        print(limitUpDetail.to_string())
        # tmp_list = limitUpDetailDataFrame.values.tolist() # 将df转换成list用于版本2中
        # print(tmp_list)
        return limitUpDetail.shape[0], limitUpDetail

    def profitLossEffectInfo(self) -> list:
        print('开始获取问财情绪数据')

        # countUplimit, uplimit = self.getWencaiData('今日涨停，剔除st', True)
        # uplimit.sort_values(uplimit.columns[8], ascending=False, inplace=True)
        # countFirstlimit, nullDataFrame = self.getWencaiData('今日连板数=1，剔除st', False)

        countUplimit = self.countUpLimit
        uplimit = self.uplimit
        topRankStock = uplimit.iloc[0]['名称']
        topRank = uplimit.iloc[0]['连续涨停天数']
        # 涨停 最高板股票 最高板位
        countFirstlimit = (uplimit['连续涨停天数'] == 1).sum()
        # 首板
        countFaillimit, faillimit = self.getWencaiData('今日炸板，剔除st', True)
        faillimit['最新涨跌幅'] = faillimit['最新涨跌幅'].astype(float)
        minFaillimit = round(faillimit['最新涨跌幅'].min() / 100, 4)
        # 炸板
        countBoardsTermination, boardsTermination = self.getWencaiData('昨日收盘涨停，今日非涨停，剔除北交所，剔除停牌，剔除S', True)
        boardsTermination['最新涨跌幅'] = boardsTermination['最新涨跌幅'].astype(float)
        minBoardsTermination = round(boardsTermination['最新涨跌幅'].min() / 100, 4)
        # 断板
        countEverDownlimit, nullDataFrame = self.getWencaiData('今日最低价=今日跌停价，剔除st', True)
        # 曾跌停
        countDownlimit, nullDataFrame = self.getWencaiData('今日跌停板，剔除st', True)
        # 跌停
        countallDayDownlimit, nullDataFrame = self.getWencaiData('今日的跌停类型是一字跌停，剔除st', False)
        # 一字跌停
        countConDownlimit, nullDataFrame = self.getWencaiData('昨日的跌停，今日的跌停，剔除st', False)
        # 连续跌停
        countUpDownlimit, nullDataFrame = self.getWencaiData('今日曾涨停，收盘跌停，剔除st', False)
        # 天地板
        countDownUplimit, nullDataFramxcwde = self.getWencaiData('今日曾跌停，收盘涨停，剔除st', False)
        # 地天板
        nullCount, preUplimit = self.getWencaiData('昨日涨停，剔除st', True)
        preUplimit['最新涨跌幅'] = preUplimit['最新涨跌幅'].astype(float)
        meanPreUplimit = round(preUplimit['最新涨跌幅'].mean() / 100, 4)
        # 昨日涨停表现
        nullCount, preConUplimit = self.getWencaiData('昨日连续涨停天数>1，剔除st', True)
        preConUplimit['最新涨跌幅'] = preConUplimit['最新涨跌幅'].astype(float)
        meanPreConUplimit = round(preConUplimit['最新涨跌幅'].mean() / 100, 4)
        # 昨日连板表现
        nullCount, preFaillimit = self.getWencaiData('昨日炸板，剔除st', True)
        preFaillimit['最新涨跌幅'] = preFaillimit['最新涨跌幅'].astype(float)
        minPreFaillimit = round(preFaillimit['最新涨跌幅'].min() / 100, 4)
        # 昨日炸板表现

        print('情绪数据获取成功')
        print(f'涨停数{countUplimit} 首板数{countFirstlimit} 板位{topRank} 炸板数{countFaillimit} 今日炸板表现{minFaillimit} '
              f'断板数{countBoardsTermination} 今日断板表现{minBoardsTermination} 曾跌停{countEverDownlimit} 跌停数{countDownlimit} '
              f'跌停数{countDownlimit} 一字跌停数{countConDownlimit} 连续跌停数{countallDayDownlimit} 天地板数{countUpDownlimit} '
              f'地天板数{countDownUplimit} 昨日涨停表现{meanPreUplimit} 昨日连板表现{meanPreConUplimit} '
              f'昨日炸板表现{minPreFaillimit} 最高板{topRankStock}')

        return [countUplimit, countFirstlimit, topRank, countFaillimit, minFaillimit, countBoardsTermination, minBoardsTermination, countEverDownlimit,
                countDownlimit, countallDayDownlimit, countConDownlimit, countUpDownlimit, countDownUplimit,
                meanPreUplimit, meanPreConUplimit, minPreFaillimit, topRankStock]

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


if __name__ != '__main__':
    pass
else:
    a = THSData()
    b, c = a.getWencaiData('今日断板，剔除北交所，剔除停牌，剔除ST', True)
    print(c)
    b, c = a.editLimitUpDetail()
