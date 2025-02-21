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
    news_sentiment_scope.set_index("日期", inplace=True)
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


if __name__ == "__main__":
    news = get_gold_news()
    print(news)
