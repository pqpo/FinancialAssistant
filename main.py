import json
import os
import streamlit as st
import componts
from datetime import datetime, timedelta
import service
import prompt

processResult = None

auth_key = os.environ.get("FA_AUTH_KEY")
if not auth_key:
    auth_key = '123'

auth_check_pass = False
if 'auth_check_pass' in st.session_state:
    auth_check_pass = st.session_state.auth_check_pass
if auth_key and not auth_check_pass:
    with st.form("auth_check"):
        check_auth_key = st.text_input("请输入访问密码", type="password")
        submitted = st.form_submit_button("提交")
        if submitted:
            if check_auth_key != auth_key:
                st.error("密码校验失败！")
                st.stop()
            else:
                st.session_state.auth_check_pass = True
        else:
            st.stop()

with st.sidebar:
    api_key = st.text_input("Api Key", os.environ.get("OPENAI_API_KEY"), type="password")
    base_url = st.text_input("Base Url", os.environ.get("OPENAI_BASE_URL"))
    mode_name = st.text_input("Model Name", os.environ.get("OPENAI_MODEL_NAME"))
    investment_prompt = st.text_area("Prompt", prompt.investment_prompt, height=300)

with st.expander("沪深300&市场情绪指数", expanded=False, icon="📈"):
    componts.show_index_news_sentiment_scope_chat()
with st.expander("恒生指数", expanded=False, icon="📈"):
    componts.show_heng_shen_chat()
# with st.expander("恒生科技指数", expanded=False, icon="📈"):
#     componts.show_hang_seng_tech_index_chat()

left, middle, right = st.columns(3)
with left:
    st.header("📢 每日新闻")
    st.caption("🚀 使用大模型总结新闻要点")
with middle:
    st.session_state.category = st.selectbox(
        "类型",
        ("All", "Stock", "CCTV", "Gold"),
        index=0
    )
with right:
    st.session_state.selectDate = st.date_input("日期", datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

date_str = st.session_state.selectDate
category = st.session_state.category
news_list = service.load_news(date_str, str(category).lower())
news_len = sum(len(df) for df in news_list) if news_list is not None else 0
with st.container(border=True, height=700):
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
    if not investment_prompt:
        st.error("请输入 Prompt!!!")
        st.stop()


def get_news_input_list():
    result = []
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

with buttonLeft:
    if st.button("📰 新闻摘要", use_container_width=True):
        check_llm_input()
        summary_input_text = get_news_input_text()
        if not summary_input_text:
            st.error("暂未查询到新闻数据!!!")
            st.stop()
        input_text = json.dumps(summary_input_text, ensure_ascii=False)
        response = service.generate_response(input_text, prompt.summary_prompt, api_key, base_url, mode_name)
        with st.status("正在提取摘要...") as status:
            st.write_stream(response)
            status.update(
                label="提取完成", state="complete", expanded=True
            )

with buttonRight:
    submitted = st.button("🚀 新闻分析", use_container_width=True)
    if submitted:
        check_llm_input()
        analysis_input_text = get_news_input_text()
        if not analysis_input_text:
            st.error("暂未查询到新闻数据!!!")
            st.stop()
        response = service.generate_response(analysis_input_text, investment_prompt, api_key, base_url, mode_name)
        with st.status("正在分析...") as status:
            st.write_stream(response)
            status.update(
                label="分析完成", state="complete", expanded=True
            )
