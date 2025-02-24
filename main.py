import json
import os
import streamlit as st
import componts
from datetime import datetime, timedelta
import service
import prompt
import pandas as pd

processResult = None

auth_key = os.environ.get("FA_AUTH_KEY")
if not auth_key:
    auth_key = '123'

auth_check_pass = True
if 'auth_check_pass' in st.session_state:
    auth_check_pass = st.session_state.auth_check_pass

if not auth_check_pass:
    with st.form("auth_check"):
        check_auth_key = st.text_input("请输入访问密码", type="password")
        submitted = st.form_submit_button("提交")
        if submitted:
            if check_auth_key != auth_key:
                st.error("密码校验失败！")
            else:
                auth_check_pass = True
                st.session_state.auth_check_pass = True
                st.rerun()
    st.stop()

st.set_page_config(layout="wide")

with st.sidebar:
    st.header("📢 每日新闻")
    st.caption("🚀 使用大模型总结新闻要点")
    api_key = st.text_input("Api Key", os.environ.get("OPENAI_API_KEY"), type="password")
    base_url = st.text_input("Base Url", os.environ.get("OPENAI_BASE_URL"))
    mode_name = st.selectbox(
        "Model Name",
        ("doubao-pro", "doubao-lite", "deepseek-r1", "deepseek-v3", "qwen-max-latest", "qwen-plus-latest"),
    )
    investment_prompt = st.text_area("Prompt", prompt.investment_prompt, height=300)


def get_news_len(news_list: list[pd.DataFrame] | None):
    return sum(len(df) for df in news_list) if news_list is not None else 0


@st.fragment
def show_news_container():
    with st.expander(f"新闻内容", expanded=True, icon="📢"):
        row_title = st.columns(2)
        with row_title[0]:
            category = st.selectbox(
                "类型",
                ("All", "Stock", "CCTV", "Gold"),
                index=0
            )
        with row_title[1]:
            date_str = st.date_input("日期", datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        news_list = service.load_news(date_str, str(category).lower())
        print(str(category).lower())
        news_len = get_news_len(news_list)
        st.session_state.news_list = news_list
        if news_len == 0:
            st.warning(f'暂无数据, 类型:{category}, 时间:{date_str}')
        else:
            with st.container(border=False, height=700):
                st.info(f'条数:{news_len}, 类型:{category}, 时间:{date_str}')
                for item in news_list:
                    componts.show_news(item)


@st.fragment
def show_global_stock_index():
    with st.expander(f"全球指数", expanded=True, icon="📈"):
        with st.container():
            show_type = st.selectbox(
                "类型",
                ("60d", "160d", "365d"),
                index=0
            )
            show_days_number = int(show_type.replace('d', ''))
            index_tabs = st.tabs(["沪深300", "恒生指数"])
            with index_tabs[0]:
                componts.show_index_news_sentiment_scope_chat(show_days_number)
            with index_tabs[1]:
                componts.show_heng_shen_chat(show_days_number)
            # with index_tabs[2]:
            #     componts.show_nasdaq_index_chat(show_days_number)


show_global_stock_index()
show_news_container()


def check_llm_input():
    error_msg = None
    if get_news_len(st.session_state.news_list) <= 0:
        error_msg = "暂未查询到新闻数据!!!"
    if not api_key:
        error_msg = "请输入 Api Key!!!"
    if not base_url:
        error_msg = "请输入 Base Url!!!"
    if not mode_name:
        error_msg = "请输入 Model Name!!!"
    if not investment_prompt:
        error_msg = "请输入 Prompt!!!"
    return error_msg


def get_news_input_list():
    result = []
    news_list = st.session_state.news_list
    if news_list is None:
        return result
    for n_item in news_list:
        for index, row in n_item.iterrows():
            result.append(json.loads(row.drop(labels=['url']).to_json(force_ascii=False)))
    return result


def get_news_input_text():
    input_list = get_news_input_list()
    if len(input_list) <= 0:
        return None
    return json.dumps(input_list, ensure_ascii=False)


buttonLeft, buttonRight = st.columns(2)
response = None
error_message = None

with buttonLeft:
    if st.button("📰 新闻摘要", use_container_width=True):
        if (error_message := check_llm_input()) is None:
            summary_input_text = get_news_input_text()
            if not summary_input_text:
                error_message = "暂未查询到新闻数据!"
            else:
                input_text = json.dumps(summary_input_text, ensure_ascii=False)
                response = service.generate_response(input_text, prompt.summary_prompt, api_key, base_url, mode_name)

with buttonRight:
    if st.button("🚀 新闻分析", use_container_width=True):
        if (error_message := check_llm_input()) is None:
            analysis_input_text = get_news_input_text()
            if not analysis_input_text:
                error_message = "暂未查询到新闻数据!"
            else:
                response = service.generate_response(analysis_input_text, investment_prompt, api_key, base_url,
                                                     mode_name)

if response is not None:
    with st.status("正在分析...") as status:
        st.write_stream(response)
        status.update(
            label="分析完成", state="complete", expanded=True
        )
elif error_message is not None:
    st.error(error_message)
