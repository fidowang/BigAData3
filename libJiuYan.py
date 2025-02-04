import json
import requests
import pandas as pd

from datetime import datetime
from libBaseStock import date_str, write_json_file


class JiuYanData(object):
    """
    韭研公社数据，用于处理韭研公社的数据获取和处理
    """

    def __init__(self):
        self.res_data: list = []

        self.act_field: list = []

        self.act_stock: list = []

        self.fieldpath = f'.\\jiuyandata\\{date_str()}_field.json'

        self.stockpath = f'.\\jiuyandata\\{date_str()}_stock.json'

        self.data_md: str = ''
        return

    def get_act_data(self, req_date: str):
        tstamp = str(int(datetime.now().timestamp() * 1000))
        cookies = {
            'SESSION': 'YWRmOTM2ZjItNmE2ZC00NGJhLWI3YmMtNDM3ZTIyODZlZmQ1',
            'UM_distinctid': '192d830026c1a5-04ad5b36cfe295-26011951-1fa400-192d830026d47f',
            'Hm_lvt_58aa18061df7855800f2a1b32d6da7f4': '1730203877,1730603052',
            'Hm_lpvt_58aa18061df7855800f2a1b32d6da7f4': '1730603232',
        }

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            # 'cookie': 'SESSION=YWRmOTM2ZjItNmE2ZC00NGJhLWI3YmMtNDM3ZTIyODZlZmQ1; UM_distinctid=192d830026c1a5-04ad5b36cfe295-26011951-1fa400-192d830026d47f; Hm_lvt_58aa18061df7855800f2a1b32d6da7f4=1730203877,1730603052; Hm_lpvt_58aa18061df7855800f2a1b32d6da7f4=1730603232',
            'origin': 'https://www.jiuyangongshe.com',
            'platform': '3',
            'priority': 'u=1, i',
            'referer': 'https://www.jiuyangongshe.com/',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'timestamp': tstamp,
            'token': '106daa1c21e90a2b249605f4c53a8ce9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        }

        json_data = {
            'date': req_date,
            'pc': 1,
        }

        response = requests.post(
            'https://app.jiuyangongshe.com/jystock-app/api/v1/action/field',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )

        resource = json.loads(response.text)
        if resource['msg'] == 'token无效，请重试':
            print(f'token无效，轻修改后重试')
            exit('token无效,程序退出')
        else:
            print(f'获取数据成功')
            self.res_data = resource['data']
            print(self.res_data)

    def act_to_json(self) -> tuple[list, object]:
        """
        将韭研的异动数据转为两个list，field_list是异动板块，包含个股，stock_list是异动个股
        :return: 两个列表第一个是异动板块即个股数据，第二个是个股数据
        """
        data_date = self.res_data.pop(0)['date']
        print(f'数据日期：{data_date}异动板块总数:{len(self.res_data)}')
        field_list: list = []
        stock_list: list = []

        for field in self.res_data:
            field_stocks: list = []
            for row in field['list']:
                if row['article']['action_info']['expound'] == '':
                    row['article']['action_info']['expound'] = 'null\nnull'
                expound_split = str.split(row['article']['action_info']['expound'], sep='\n', maxsplit=1)

                stock_cont: dict = {
                    'code': row['code'],
                    'name': row['name'],
                    'act_date': data_date,
                    'briefReason': str.split(expound_split[0], sep='+'),
                    'detailReason': str.split(expound_split[1], sep='\n'),
                    'fieldName': field['name'],
                    'fieldReason': field['reason']
                }
                field_stocks.append(stock_cont)
                stock_list.append(stock_cont)

            field_cont: dict = {
                'id': field['action_field_id'],
                'name': field['name'],
                'act_date': field['date'],
                'reason': field['reason'],
                'count': field['count'],
                'stocks': field_stocks
            }
            field_list.append(field_cont)
            self.act_field = field_list

        jiuyanactstockdataframe = pd.DataFrame(stock_list)
        print(jiuyanactstockdataframe.to_string())

        return field_list, jiuyanactstockdataframe

    def data_wrt(self):
        write_json_file(path=self.fieldpath, json_obj=self.act_field)
        write_json_file(path=self.stockpath, json_obj=self.act_stock)

    def json_to_md(self, req_date: str, jsondat: list | dict):
        """
        用于将韭研异动数据整理成markdown文本报告，目前暂时剔除ST板块
        :param req_date:目标数据日期
        :param jsondat: 韭研下载的json文件，必须是字典或者列表
        """
        markdown_output = ''
        for field in jsondat:
            stocks = field['stocks']
            if field['name'] == 'ST板块':
                continue
            else:
                markdown_output += '### 异动板块：' + field['name'] + ' ' + '数量：' + str(field['count']) + '\n'
                if field['reason']:
                    markdown_output += '板块异动原因：' + field['reason'] + '\n\n'

                for stock in stocks:
                    markdown_output += '#### ' + stock['code'] + ' #' + stock['name'].replace('*', '') \
                                       + ' ' + stock['num'] + '\n'
                    markdown_output += '##### 异动概念：' + ' #' + ' #'.join(stock['act_reason']) + '\n'
                    markdown_output += '\n'.join(stock['expound']) + '\n\n'

        self.data_md = markdown_output

        # with open(f'E:\\ARCHIVE\\Documents\\ObVaults\\随身笔记\\{req_date}.md', 'w', encoding='UTF-8') as file:
        #     file.write(markdown_output)
        # file.close()


if __name__ != '__main__':
    pass
else:
    JiuYanDataTest = JiuYanData()
    JiuYanDataTest.get_act_data('2024-6-3')
    JiuYanDataTest.act_to_json()
