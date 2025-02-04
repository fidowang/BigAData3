import libJiuYan
import libTHS
import libBaseStock

from libTHS import qingxushuju, getIndexInfo

if __name__ != '__main__':
    pass
else:
    bigA = libBaseStock.BaseData()
    THS = libTHS.THSData()
    JiuYan = libJiuYan.JiuYanData()

    JiuYan.get_act_data(bigA.date_str)
    jy_act_field, jyStocks = JiuYan.act_to_json()
    # JiuYan.data_wrt()

    bigA.hs_amount, bigA.indexSH = getIndexInfo()
    bigA.up_counts, bigA.zero_counts, bigA.down_counts = THS.updown_count
    bigA.zt_counts, bigA.thsStocks = THS.editLimitUpDetail()
    bigA.stock_list = bigA.ths_match_jy(thsdata=bigA.thsStocks, jydata=jyStocks)
    bigA.count_zt, bigA.count_sb, bigA.count_zb, bigA.count_dt, bigA.count_qb, bigA.count_dje = qingxushuju()
    bigA.xls_edit()
