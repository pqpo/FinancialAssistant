import akshare as ak
import pandas as pd
from akshare.request import make_request_with_retry_json
from datetime import datetime
from pathlib import Path


# cctv 发言稿
def get_cctv_news(date_str: str):
    print(f"start get_cctv_news: {date_str}")
    cctv_news = ak.news_cctv(date=date_str)
    cctv_news.rename(columns={"date": "pub_time"}, inplace=True)
    cctv_news['url'] = ''
    cctv_news['category'] = 'cctv'
    return cctv_news[['category', 'pub_time', 'title', 'content', 'url']]


# 黄金新闻
def get_gold_news(date_str: str):
    print(f"start get_gold_news: {date_str}")
    gold_news = ak.futures_news_shmet(symbol="贵金属")  # 黄金新闻
    gold_news.rename(columns={"发布时间": "pub_time", "内容": "content"}, inplace=True)
    gold_news["pub_time"] = pd.to_datetime(
        gold_news["pub_time"], errors="coerce", unit="ms"
    ).dt.strftime('%Y%m%d')
    # 处理可能没有标题的情况
    gold_news['title'] = gold_news['content'].str.extract(r'^【(.*?)】').replace("【").replace("】")  # 严格从开头匹配
    gold_news['content'] = gold_news['content'].str.replace(r'^【.*?】\s*', '', regex=True)  # 删除标题及可能存在的空格
    # 填充空值
    gold_news['title'] = gold_news['title'].fillna('无标题')
    gold_news = gold_news[gold_news['content'].str.strip().astype(bool)]
    gold_news['url'] = ''
    gold_news['category'] = 'gold'
    return gold_news[gold_news['pub_time'] == date_str][['category', 'pub_time', 'title', 'content', 'url']]


# 财经新闻
def get_stock_news_main_cx(date_str: str) -> pd.DataFrame:
    print(f"start get_stock_news_main_cx: {date_str}")
    url = "https://cxdata.caixin.com/api/dataplus/sjtPc/jxNews"
    params = {
        "pageNum": "1",
        "pageSize": "50",
        "showLabels": "true",
    }
    data_json = make_request_with_retry_json(url, params=params)
    temp_df = pd.DataFrame(data_json["data"]["data"])
    temp_df = temp_df[["tag", "summary", "pubTime", "url"]]
    temp_df.columns = ["tag", "summary", "pub_time", "url"]
    temp_df["pub_time"] = pd.to_datetime(
        temp_df["pub_time"], errors="coerce", unit="ms"
    ).dt.strftime('%Y%m%d')
    temp_df['category'] = 'stock'
    temp_df.rename(columns={'tag': 'title', 'summary': 'content'}, inplace=True)
    return temp_df[temp_df['pub_time'] == date_str][['category', 'pub_time', 'title', 'content', 'url']]


def fetch(category: str, date_str: str):
    df = None
    if category == 'cctv':
        df = get_cctv_news(date_str)
    if category == 'gold':
        df = get_gold_news(date_str)
    if category == 'stock':
        df = get_stock_news_main_cx(date_str)
    if df is not None:
        data_path = Path.cwd() / "data" / date_str / f"{category}.csv"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        print(f'save dir: {data_path}')
        df.to_csv(data_path, index=False)


if __name__ == "__main__":
    date = datetime.now().strftime('%Y%m%d')
    for c in ['cctv', 'gold', 'stock']:
        try:
            fetch(c, date)
        except Exception as e:
            print(f'spider error, {c}, error: {e}')
