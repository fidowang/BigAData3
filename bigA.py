import libJiuYan
import libTHS
import libBaseStock
import libXuanGuTong

from libTHS import getIndexInfo

if __name__ != '__main__':
    pass
else:
    bigA = libBaseStock.BaseData()
    THS = libTHS.THSData()
    JiuYan = libJiuYan.JiuYanData()
    XGT = libXuanGuTong.XuanGuTongData()

    JiuYan.get_act_data(bigA.date_str)
    jy_act_field, jyStocks = JiuYan.act_to_json()
    # JiuYan.data_wrt()

    bigA.zt_counts, bigA.thsStocks = THS.editLimitUpDetail()
    bigA.stock_list = bigA.ths_match_jy(thsdata=bigA.thsStocks, jydata=jyStocks)

    bigA.marketIndexInfo = getIndexInfo()
    bigA.redGreenCount = XGT.riseFallCounts()
    bigA.marketMoodData = THS.profitLossEffectInfo()
    bigA.marketDetialInfo = [bigA.dateToExcelQuery,] + bigA.marketIndexInfo + bigA.redGreenCount + bigA.marketMoodData
    print(bigA.marketDetialInfo)
    bigA.xls_edit()
