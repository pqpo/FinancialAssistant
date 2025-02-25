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

api_key = os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("OPENAI_BASE_URL")


def get_news_len(news_list: list[pd.DataFrame] | None):
    return sum(len(df) for df in news_list) if news_list is not None else 0


@st.fragment
def show_news_container(container, category):
    print("refresh news")
    date_str = st.date_input("日期", datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    with container.container():
        news_list = service.load_news(date_str, str(category).lower())
        print(str(category).lower())
        news_len = get_news_len(news_list)
        st.session_state.news_list = news_list
        if news_len == 0:
            st.warning(f'暂无数据, 类型:{category}, 时间:{date_str}')
        else:
            with st.container(border=False, height=800):
                st.info(f'条数:{news_len}, 类型:{category}, 时间:{date_str}')
                for item in news_list:
                    componts.show_news(item)


@st.fragment
def show_global_stock_index(i_container, s_type):
    print("refresh stock index")
    with i_container.container():
        show_days_number = int(s_type.replace('d', ''))
        index_tabs = st.tabs(["沪深300", "恒生指数"])
        with index_tabs[0]:
            componts.show_index_news_sentiment_scope_chat(show_days_number)
        with index_tabs[1]:
            componts.show_heng_shen_chat(show_days_number)
        # with index_tabs[2]:
        #     componts.show_nasdaq_index_chat(show_days_number)


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
    if not real_prompt:
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


with st.expander(f"全球指数", expanded=False, icon="📈"):
    show_type = st.selectbox(
        "类型",
        ("30d", "90d", "160d", "365d"),
        index=0
    )
    index_container = st.container(border=False)

with st.expander(f"新闻内容", expanded=True, icon="📢"):
    s_category = st.selectbox(
        "类型",
        ("All", "Stock", "CCTV", "Gold"),
        index=0
    )
    news_container = st.container(border=False)

response = None
error_message = None

with st.sidebar:
    st.header("📢 每日新闻")
    st.caption("🚀 使用大模型总结新闻要点")
    show_news_container(news_container.empty(), s_category)
    mode_name = st.selectbox(
        "Model Name",
        ("doubao-pro", "doubao-lite", "deepseek-r1", "deepseek-v3", "qwen-max-latest", "qwen-plus-latest"),
    )
    prompt_type = st.selectbox(
        "Preset",
        ("提取摘要", "财经分析", "自定义"),
    )
    selected_prompt = ""
    if prompt_type == "提取摘要":
        selected_prompt = prompt.summary_prompt
    elif prompt_type == "财经分析":
        selected_prompt = prompt.investment_prompt
    real_prompt = st.text_area("Prompt", selected_prompt, height=300)
    if st.button("🚀 新闻分析", use_container_width=True):
        if (error_message := check_llm_input()) is None:
            analysis_input_text = get_news_input_text()
            if not analysis_input_text:
                error_message = "暂未查询到新闻数据!"
            else:
                response = service.generate_response(analysis_input_text, real_prompt, api_key, base_url,
                                                     mode_name)


if response is not None:
    with st.status("正在分析...") as status:
        st.write_stream(response)
        status.update(
            label="分析完成", state="complete", expanded=True
        )
elif error_message is not None:
    st.error(error_message)

# 比较耗时，放在最后加载
show_global_stock_index(index_container, show_type)
