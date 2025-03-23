import json
import requests
import datetime


class XuanGuTongData(object):
    def __init__(self):
        return

    def riseFallCounts(self) -> list:
        print('开始获取红绿家数')
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://xuangutong.com.cn',
            'priority': 'u=1, i',
            'referer': 'https://xuangutong.com.cn/dingpan',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }
        response = requests.get(
            'https://flash-api.xuangubao.com.cn/api/market_indicator/line?fields=rise_count,fall_count',
            headers=headers,
        )
        riseFallCountResource = json.loads(response.text)
        if riseFallCountResource['message'] == 'OK':
            lastRiseFallData = riseFallCountResource['data'][-1]
        else:
            exit('获取涨跌家数数据失败')
        dt = datetime.datetime.fromtimestamp(lastRiseFallData['timestamp'])
        if dt.hour != 15:
            exit('涨跌家数未找到收盘数据')

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://xuangutong.com.cn',
            'priority': 'u=1, i',
            'referer': 'https://xuangutong.com.cn/dingpan',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }
        response = requests.get('https://flash-api.xuangubao.com.cn/api/market_indicator/pcp_distribution', headers=headers)
        pcpDistributionResource = json.loads(response.text)
        if pcpDistributionResource['message'] == 'OK':
            zeroCount = pcpDistributionResource['data']['0']
        else:
            exit('获取涨跌分布数据失败')

        print(f'红绿家数是上涨：{lastRiseFallData["rise_count"]}, 平盘：{zeroCount}, 下跌：{lastRiseFallData["fall_count"]}')
        return [lastRiseFallData['rise_count'], zeroCount, lastRiseFallData['fall_count']]


if __name__ != '__main__':
    pass
else:
    xuanGuTong = XuanGuTongData()
    red, zero, green = xuanGuTong.riseFallCounts()