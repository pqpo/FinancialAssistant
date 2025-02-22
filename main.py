import streamlit as st
import componts
from datetime import datetime
import service

default_prompt = "下面是最近发生的新闻，帮我总结提取一下新闻内容，通过你的阅读需要你给出判断是否会对某只或者某类股票造成影响，以及对黄金价格走势的影响。影响需要给出新闻依据。"

processResult = None

with st.sidebar:
    api_key = st.text_input("Api Key", type="password")
    base_url = st.text_input("Base Url", "https://api.deepseek.com")
    mode_name = st.text_input("Model Name", "deepseek-r1")
    prompt = st.text_area("Prompt", default_prompt, height=300)

with st.expander("沪深300&市场情绪指数", expanded=False, icon="🔥"):
    componts.show_index_news_sentiment_scope_chat()

left, middle, right = st.columns(3)
with left:
    st.header("📰每日新闻")
    st.caption("🚀 使用大模型总结新闻要点")
with middle:
    st.session_state.category = st.selectbox(
        "类型",
        ("All", "Stock", "CCTV", "Gold"),
        index=0
    )
with right:
    st.session_state.selectDate = st.date_input("日期", datetime.now()).strftime("%Y%m%d")

date_str = st.session_state.selectDate
category = st.session_state.category
news_list = service.load_news(date_str, str(category).lower())
news_len = sum(len(df) for df in news_list) if news_list is not None else 0
with st.container(border=True, height=500):
    if news_list is None:
        st.error(f'暂无数据：{date_str}, {category}')
    else:
        st.success(f'查询到{news_len}条记录')
        for item in news_list:
            componts.show_news(item)


def check_llm_input():
    if news_len <= 0:
        st.error("暂未查询到新闻数据!!!")
        st.stop()
    if not api_key:
        st.error("请输入 Api Key!!!")
        st.stop()
    if not base_url:
        st.error("请输入 Base Url!!!")
        st.stop()
    if not mode_name:
        st.error("请输入 Model Name!!!")
        st.stop()
    if not prompt:
        st.error("请输入 Prompt!!!")
        st.stop()


submitted = st.button("🚀 新闻分析", use_container_width=True)
if submitted:
    check_llm_input()
    st.info(prompt)
