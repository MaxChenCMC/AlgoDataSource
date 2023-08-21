import json, time, datetime, pytz, requests, pandas as pd
from io import StringIO
from bs4 import BeautifulSoup

def AlgoSource(localDate: str) -> tuple[int, int, int, int, int, int, int, int, int, int, float, float, float, float, float, int, float, float]:
    '''
    檢查 爬蟲日(BaseDate) == 期貨日(srcDate) == 加權API日 == PutCallRatio日
    '''
    url1 = "https://www.twse.com.tw/fund/BFI82U?response=csv&dayDate=" + pd.to_datetime(localDate).strftime("%Y%m%d") +"&type=day"
    url2 = "https://www.taifex.com.tw/cht/3/futContractsDate"
    url3 = "https://www.taifex.com.tw/cht/3/futDailyMarketReport"
    url4 = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch=tse_t00.tw"
    url5 = "https://www.taifex.com.tw/cht/3/pcRatio"
    url2Date = pd.read_html(url2)[2].loc[0,0][-10:]
    url3Date = pd.read_html(url3)[2].iloc[2,0][15:25]
    url4Date = pd.to_datetime(requests.get(url4).json()["msgArray"][0].get("d")).strftime("%Y/%m/%d")
    url5Date = datetime.datetime.strptime(pd.read_html(url5)[3].iloc[0,0], "%Y/%m/%d").strftime("%Y/%m/%d")

    if len(set([localDate, url2Date, url3Date, url4Date, url5Date])) != 1:
        print(f"爬蟲與資料來源日期{set([localDate, url2Date, url3Date, url4Date, url5Date])}，若不一致需人工檢查")

    else:
        # 
        df = pd.read_csv(StringIO(requests.get(url1).text), header = 1).dropna(how = 'all', axis = 1).dropna(how = 'any')
        institution = int(df.loc[3, '買賣差額'].replace(',', '')) # 外資及陸資(不含自營)
        trust = int(df.loc[2, '買賣差額'].replace(',', '')) # 投信

        #
        response = requests.post(url2, data = {'queryDate': localDate, "queryType": 1})
        soup = BeautifulSoup(response.text,features = "html.parser")
        table = soup.find( "table", class_ = "table_f")
        tx = table.find_all('tr')[5].find_all('td')
        txnet = int([i.text.strip() for i in tx][4].replace(',', ''))
        txoi = int([i.text.strip() for i in tx][10].replace(',', ''))
        mtx = table.find_all('tr')[14].find_all('td')
        mtxnet = int([i.text.strip() for i in mtx][4].replace(',', ''))
        mtxoi = int([i.text.strip() for i in mtx][10].replace(',', ''))

        #
        txf_ohlc = pd.read_html(url3)[2].loc[4,:][[2,3,4,5,9]].values.tolist()
        txf_ohlc = [int(i) for i in txf_ohlc]

        #
        src = requests.get(url4).json()["msgArray"][0]
        tse_ohlcv = [float(src.get(i)) for i in ["o","h","l","z"]]
        tse_ohlcv.append(float(src.get("v")) / 100)

        #
        PutCall = pd.read_html(url5)[3:4][0].iloc[0][['買賣權成交量比率%',"買賣權未平倉量比率%"]].to_list()
        
        return print((institution, trust, txnet, txoi, mtxnet, mtxoi) + tuple(txf_ohlc) + tuple(tse_ohlcv) + tuple(PutCall))

AlgoSource(
    # "2023/08/21"
    datetime.datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y/%m/%d")
    )
