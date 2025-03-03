import streamlit as st
import akshare as ak
import pandas as pd
from akshare.request import make_request_with_retry_json
from datetime import datetime


# cctv 新闻
@st.cache_data(ttl='0.5d')
def get_cctv_news():
    print("load get_cctv_news!")
    today = datetime.now().strftime('%Y%m%d')
    cctv_news = ak.news_cctv(date=today)
    cctv_news.rename(columns={"date": "pub_time"}, inplace=True)
    cctv_news["pub_time"] = pd.to_datetime(
        cctv_news["pub_time"].astype(str), format='%Y%m%d', errors="coerce"
    )
    cctv_news['url'] = ''
    return cctv_news


# 黄金新闻
@st.cache_data(ttl='0.5d')
def get_gold_news():
    print("load gold_news data!")
    gold_news = ak.futures_news_shmet(symbol="贵金属")  # 黄金新闻
    gold_news.rename(columns={"发布时间": "pub_time", "内容": "content"}, inplace=True)
    gold_news["pub_time"] = pd.to_datetime(
        gold_news["pub_time"], errors="coerce", unit="ms"
    )
    # 处理可能没有标题的情况
    gold_news['title'] = gold_news['content'].str.extract(r'^【(.*?)】')  # 严格从开头匹配
    gold_news['content'] = gold_news['content'].str.replace(r'^【.*?】\s*', '', regex=True)  # 删除标题及可能存在的空格
    # 填充空值
    gold_news['title'] = gold_news['title'].fillna('无标题')
    gold_news = gold_news[gold_news['content'].str.strip().astype(bool)]
    gold_news = gold_news.sort_values('pub_time', ascending=False)
    gold_news['url'] = ''
    return gold_news.head(150)


# A股新闻情绪指数
@st.cache_data(ttl='0.5d')
def get_index_news_sentiment_scope():
    print("load index_news_sentiment_scope data!")
    news_sentiment_scope = ak.index_news_sentiment_scope()
    return news_sentiment_scope


# ak.stock_news_main_cx()
# 财经新闻
@st.cache_data(ttl='0.5d')
def get_stock_news_main_cx() -> pd.DataFrame:
    print("load stock_news_main_cx data!")
    url = "https://cxdata.caixin.com/api/dataplus/sjtPc/jxNews"
    params = {
        "pageNum": "1",
        "pageSize": "150",
        "showLabels": "true",
    }
    data_json = make_request_with_retry_json(url, params=params)
    temp_df = pd.DataFrame(data_json["data"]["data"])
    temp_df = temp_df[["tag", "summary", "pubTime", "url"]]
    temp_df.columns = ["tag", "summary", "pub_time", "url"]
    temp_df["pub_time"] = pd.to_datetime(
        temp_df["pub_time"], errors="coerce", unit="ms"
    )
    temp_df = temp_df.sort_values('pub_time', ascending=False)
    temp_df.rename(columns={'tag': 'title', 'summary': 'content'}, inplace=True)
    return temp_df.to_json()


@st.cache_data(ttl='0.5d')
def nasdaq_index() -> pd.DataFrame:
    print("load nasdaq_index data!")
    url = "https://api.investing.com/api/financialdata/14958/historical/chart/?interval=P1W&pointscount=160"
    data_json = make_request_with_retry_json(url, params={}, headers={
        ":authority":"api.investing.com",
        "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding":"gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    })
    temp_df = pd.DataFrame(data_json["data"])
    temp_df = temp_df[[0, -3]]
    temp_df.columns = ['date', 'stock_index']
    temp_df['date'] = pd.to_datetime(temp_df['date'], unit='ms')
    temp_df['date'] = temp_df['date'].dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
    return temp_df


@st.cache_data(ttl='0.5d')
def hang_seng_index() -> pd.DataFrame:
    print("load hang_seng_index data!")
    url = "https://www.hsi.com.hk/data/eng/indexes/00001.00/chart.json"
    data_json = make_request_with_retry_json(url, params={})
    temp_df = pd.DataFrame(data_json["indexLevels-1y"], columns=['date', 'stock_index'])
    temp_df['date'] = pd.to_datetime(temp_df['date'], unit='ms')
    temp_df['date'] = temp_df['date'].dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
    return temp_df


@st.cache_data(ttl='0.5d')
def hang_seng_tech_index() -> pd.DataFrame:
    print("load hang_seng_tech_index data!")
    url = "https://www.hsi.com.hk/data/eng/indexes/02083.00/chart.json"
    data_json = make_request_with_retry_json(url, params={})
    temp_df = pd.DataFrame(data_json["indexLevels-1y"], columns=['date', 'stock_index'])
    temp_df['date'] = pd.to_datetime(temp_df['date'], unit='ms')
    temp_df['date'] = temp_df['date'].dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
    return temp_df


if __name__ == "__main__":
    news = hang_seng_index()
    print(news)
