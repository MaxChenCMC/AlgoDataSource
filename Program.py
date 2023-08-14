import json, time, datetime, requests, pandas as pd
from io import StringIO
from bs4 import BeautifulSoup


def AlgoSource(BaseDate: str) -> tuple[int, int, int, int, int, int, int, int, int, int, float, float, float, float, float, int, float, float]:
    '''
    5 source url: 現貨買賣超、期貨IO、TXF_OHLCV 、TWSE_OHLCV、PutCallRatio
    '''
    srcDate = pd.read_html('https://www.taifex.com.tw/cht/3/futContractsDate')[2].loc[0,0][-10:]
    if datetime.date.today().weekday() <= 4 and BaseDate == srcDate:

        r = requests.get('https://www.twse.com.tw/fund/BFI82U?response=csv&dayDate='
            + datetime.date.today().strftime("%Y%m%d")
            + '&type=day')
        if r.text != "\r\n":
            df = pd.read_csv(StringIO(r.text), header = 1).dropna(how = 'all', axis = 1).dropna(how = 'any')
            institution = int(df.loc[3, '買賣差額'].replace(',', '')) # 外資及陸資(不含自營)
            trust = int(df.loc[2, '買賣差額'].replace(',', '')) # 投信
        else:
            print("三大法人買賣金額統計表 來源有誤")


        # srcDate = pd.read_html('https://www.taifex.com.tw/cht/3/futContractsDate')[2].loc[0,0][-10:]
        if BaseDate == srcDate :
            myobj = {'queryDate': BaseDate, "queryType": 1}
            response = requests.post("https://www.taifex.com.tw/cht/3/futContractsDate", data = myobj)
            soup = BeautifulSoup(response.text,features = "html.parser")
            table = soup.find( "table", class_ = "table_f")
            tx = table.find_all('tr')[5].find_all('td')
            txnet = int([i.text.strip() for i in tx][4].replace(',', ''))
            txoi = int([i.text.strip() for i in tx][10].replace(',', ''))
            mtx = table.find_all('tr')[14].find_all('td')
            mtxnet = int([i.text.strip() for i in mtx][4].replace(',', ''))
            mtxoi = int([i.text.strip() for i in mtx][10].replace(',', ''))
        else:
            print("期貨契約 來源有誤")


        if BaseDate in pd.read_html("https://www.taifex.com.tw/cht/3/futDailyMarketReport")[2].iloc[2,0]:
            txf_ohlc = pd.read_html("https://www.taifex.com.tw/cht/3/futDailyMarketReport")[2].loc[4,:][[2,3,4,5,9]].values.tolist()
            txf_ohlc = [int(i) for i in txf_ohlc]
        else:
            print("臺股期貨(TX)行情表 來源有誤")


        url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch=tse_t00.tw"
        url_json = requests.get(url).json()
        src = url_json["msgArray"][0]
        if BaseDate == datetime.datetime.strptime(src.get("d"), "%Y%m%d").strftime("%Y/%m/%d") :
            tse_ohlcv = [float(src.get(i)) for i in ["o","h","l","z"]]
            tse_ohlcv.append(float(src.get("v")) / 100)
        else:
            print("加權指數API 來源有誤")


        src5 = pd.read_html("https://www.taifex.com.tw/cht/3/pcRatio")
        if BaseDate == datetime.datetime.strptime(src5[3].iloc[0,0], "%Y/%m/%d").strftime("%Y/%m/%d"):
            PutCall = src5[3:4][0].iloc[0][['買賣權成交量比率%',"買賣權未平倉量比率%"]].to_list()
        else:
            print("臺指選擇權Put/Call比 來源有誤")


    else:
        print("週末或休市時爬蟲資料會缺失")

    return print((institution, trust, txnet, txoi, mtxnet, mtxoi) + tuple(txf_ohlc) + tuple(tse_ohlcv) + tuple(PutCall))



if __name__ == "__main__":
    AlgoSource(datetime.date.today().strftime("%Y/%m/%d"))