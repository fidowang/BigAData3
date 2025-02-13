import json

from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import NamedStyle


def read_json_file(path: str) -> list | dict:
    with open(path, 'r', encoding='UTF-8') as jsonfile:
        json_data = json.load(jsonfile)
    jsonfile.close()
    return json_data


def write_json_file(path: str, json_obj: list | dict):
    with open(path, 'w', encoding='UTF-8') as file:
        json.dump(json_obj, file, ensure_ascii=False, indent=4)
    file.close()


def date_to_xls_num(date=datetime.today().date()) -> int:
    if isinstance(date, str):
        dt1 = datetime.strptime(date, '%Y-%m-%d').date()
        # dt1 = dt1.date()
    else:
        dt1 = date
    return dt1 - datetime(1900, 1, 1).date() + timedelta(days=2)


def date_str(dt: str = datetime.today().date().strftime('%Y-%m-%d')) -> str:
    return dt


class BaseData(object):
    def __init__(self):
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
            '韭研原因': 11,  # 同花顺导出数据中该列为连续涨停，后变更为韭研原因
            '开票涨幅': 12,
            '竞价金额': 13
        }

        self.title_market_map: Dict[str, int] = {
            '日期': 0,
            '成交量': 1,
            '上涨数': 2,
            '下跌数': 3,
            '涨停数（不含st）': 4,
            '首板数': 5,
            '炸板数': 6,
            '跌停数': 7,
            '翘跌停': 8,
            '高额交易数': 9,
            '市场高标': 10,
            '最高板位': 11,
            '连板成功率': 12,
            '连板率': 13,
            '炸板率': 14
        }

        self.date_str = date_str()

        self.today_xls_num = date_to_xls_num()

        self.bigA_path = '.\\bigAReview.xlsx'

        self.bigA_back = f'.\\review_backup\\bigAReview_{self.date_str}.xlsx'

        # 以下一次为上涨数、平盘数、下跌数、涨停数、涨停股票列表、沪深两市成交额
        self.redGreenCount: list = []

        self.zt_counts: int = 0

        self.stock_list: List[list] = []

        self.hs_amount: int = 0

        self.count_zt: int = 0
        # 同花顺问财涨停数

        self.count_sb: int = 0
        # 同花顺问财首板数

        self.count_zb: int = 0
        # 同花顺问财炸板数

        self.count_dt: int = 0
        # 同花顺问财跌停数

        self.count_qb: int = 0
        # 同花顺问财撬板数

        self.count_dje: int = 0
        # 同花顺问财成交额大于15数
        self.marketMoodData: list = []

    def ths_match_jy(self, thsdata: object, jydata: object) -> list:
        """
        匹配同花顺和韭研的数据，输出结果是同花顺数据，用于完成bigAReview
        :param ths_data: 同花顺导入的数据
        :param jy_data: 韭研导入的数据
        :return: 输出同花顺个股数据列表，用于填入bigAReview
        """
        print('开始匹配同花顺和韭研公社涨停股数据')
        compiledStocksData = pd.merge(thsdata, jydata[['code', 'fieldName', 'briefReason']], left_on='代码', right_on='code', how='left')
        compiledStocksData['原因类别'] = compiledStocksData['原因类别'] + '||' + compiledStocksData['briefReason'].apply(lambda x: '+'.join(x) if isinstance(x, list) else str(x))
        compiledStocksData.drop(columns='code', axis='columns', inplace=True)
        compiledStocksData.drop(columns='briefReason', axis='columns', inplace=True)

        tmpResultData = compiledStocksData.values.tolist()
        # title_row = self.title_row_map
        # for x in ths_data:
        #     for y in jy_data:
        #         if x[title_row['名称']] == y['name']:
        #             x[title_row['韭研原因']] = y['action_field_name']
        #     if x[title_row['韭研原因']] == '':
        #         print(f'{x[title_row['代码']]} {x[title_row['名称']]}匹配不到韭研异动个股')
        #     # print(x)
        print('数据匹配完成')
        print(compiledStocksData.to_string())
        return tmpResultData

    def xls_edit(self) -> None:
        # book_path = self.bigA_path
        print('开始打开bigAReview文件')
        book_path = load_workbook(self.bigA_path)
        # book_path = load_workbook("new.xlsx")
        print('文件正在进行备份')
        book_path.save(self.bigA_back)
        print('备份完成，开始写入数据')

        # self.marketinfo_wrt(book_path)
        self.marketInfoWrite(book_path)
        self.limitup_wrt(book_path, self.zt_counts, self.stock_list)

        book_path.save(self.bigA_path)
        # book_path.save("new.xlsx")
        print('数据写入完成')

    def limitup_wrt(self, book_review: object, limitup_counts: int, limit_up_stock: list) -> None:

        print('limitup_wrt 开始运行')
        print('涨停板表格数据开始写入')
        sheet_limituplist = book_review['涨停板']
        sheet_limituplist.insert_rows(2, limitup_counts)
        style_date = '日期'
        style_code = '代码'
        style_time = '时间'
        style_million = '百万'
        if '百分比' not in book_review.named_styles:
            print("无\"百分比\"样式，需建立样式")
            style_percent = NamedStyle(name='百分比')
            style_percent.number_format = "0.00%"
        else:
            style_percent = '百分比'

        if '亿元' not in book_review.named_styles:
            print("无\"亿元\"样式，需建立样式")
            style_currency = NamedStyle(name='亿元')
            style_currency.number_format = "0!.00,,\"亿\""
        else:
            style_currency = '亿元'

        for irow in range(0, limitup_counts):
            for icol in range(0, len(limit_up_stock[0])):
                sheet_limituplist.cell(irow + 2, icol + 1).value = limit_up_stock[irow][icol]
                match icol:
                    case 0:  # 对部分列进行格式化
                        sheet_limituplist.cell(irow + 2, icol + 1).style = style_date
                    case 1:
                        sheet_limituplist.cell(irow + 2, icol + 1).style = style_code
                    case 6:
                        sheet_limituplist.cell(irow + 2, icol + 1).style = style_time
                    case 7:
                        sheet_limituplist.cell(irow + 2, icol + 1).style = style_time
                    case 9:
                        sheet_limituplist.cell(irow + 2, icol + 1).style = style_currency
                    case 10:
                        sheet_limituplist.cell(irow + 2, icol + 1).style = style_million
                    case 11:
                        sheet_limituplist.cell(irow + 2, icol + 1).style = style_currency
                    case 12:
                        sheet_limituplist.cell(irow + 2, icol + 1).style = style_percent
                    case 13:
                        sheet_limituplist.cell(irow + 2, icol + 1).style = style_percent
        # 日期0 代码1 名称2 几天几板3 连续涨停天数4 原因类别5 首次涨停时间6 最终涨停时间7 现价8 金额9 竞价金额10 自由流值11 涨幅12 开盘涨幅13 韭研异动板块14 异动解析15

        print('涨停板表格数据已写入')

    def marketinfo_wrt(self, book_review: object) -> None:
        print('marketinfo_wrt 开始运行')
        date_to_wrt = date_to_xls_num()
        sheet_market = book_review['市场']
        style_weekdate: str = '日期周'
        style_percent: str = '百分比'

        for row in sheet_market.iter_rows(min_col=1, max_col=1):
            # print(f'{row[0].value}')
            if row[0].value == date_to_wrt:
                exit('检测到今日日期，请检查今日数据是否已写入')
            else:
                row_to_wrt: int = row[0].row + 1

        sheet_market.cell(row_to_wrt, 1).value = date_to_wrt
        sheet_market.cell(row_to_wrt, 1).style = style_weekdate
        sheet_market.cell(row_to_wrt, 2).value = self.hs_amount
        sheet_market.cell(row_to_wrt, 3).value = self.up_counts
        sheet_market.cell(row_to_wrt, 4).value = self.zero_counts
        sheet_market.cell(row_to_wrt, 5).value = self.down_counts
        sheet_market.cell(row_to_wrt, 6).value = self.count_zt
        sheet_market.cell(row_to_wrt, 7).value = self.count_sb
        sheet_market.cell(row_to_wrt, 8).value = self.count_zb
        sheet_market.cell(row_to_wrt, 9).value = self.count_dt
        sheet_market.cell(row_to_wrt, 10).value = self.count_qb
        sheet_market.cell(row_to_wrt, 11).value = self.count_dje

        sheet_market.cell(row_to_wrt, 12).value = f'=VLOOKUP($A{row_to_wrt},涨停板!$A:$E,3,FALSE)'
        sheet_market.cell(row_to_wrt, 13).value = f'=VLOOKUP($A{row_to_wrt},涨停板!$A:$E,5,FALSE)'
        sheet_market.cell(row_to_wrt, 14).value = f'=(F{row_to_wrt}-G{row_to_wrt})/F{row_to_wrt - 1}'
        sheet_market.cell(row_to_wrt, 15).value = f'=(F{row_to_wrt}-G{row_to_wrt})/F{row_to_wrt}'
        sheet_market.cell(row_to_wrt, 16).value = f'=H{row_to_wrt}/(F{row_to_wrt}+H{row_to_wrt})'
        sheet_market.cell(row_to_wrt, 14).style = style_percent
        sheet_market.cell(row_to_wrt, 15).style = style_percent
        sheet_market.cell(row_to_wrt, 16).style = style_percent

    def marketInfoWrite(self, book_review: object) -> None:
        print('marketinfo_wrt 开始运行')
        dateToWrite = date_to_xls_num()
        self.marketMoodData.insert(0, dateToWrite)
        marketInfoSheet = book_review['市场']
        styleWeekdate: str = '日期周'
        stylePercent: str = '百分比'
        for row in marketInfoSheet.iter_rows(min_col=1, max_col=1):
            # print(f'{row[0].value}')
            if row[0].value == dateToWrite:
                exit('检测到今日日期，请检查今日数据是否已写入')
            else:
                rowToWrite: int = row[0].row + 1
        marketInfoSheet.append(self.marketMoodData)

if __name__ != '__main__':
    pass
