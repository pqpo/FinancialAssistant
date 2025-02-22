import json
import os
import streamlit as st
import componts
from datetime import datetime, timedelta
import service

default_prompt = f"""
你是一位资深财经分析师，擅长从海量信息中快速识别投资机会与潜在风险, 并给出相应的投资建议。请基于我提供的新闻数据，执行以下分析：
1. 关键事件筛选
识别影响宏观经济/行业/资本市场的政策类新闻（如货币政策、行业规范）
标记涉及贵金属供需的核心事件（如矿山罢工、新能源需求）
捕捉地缘政治/国际经贸重大变动（如中美关税、战争风险）
2. 影响链分析
政策类：使用「政策工具→流动性变化→行业传导」框架
（例：降准→银行放贷能力+15%→基建/房地产板块受益）
贵金属类：构建「供给端事件+需求端动向+美元指数」三维评估
国际事件：标注受影响的具体商品/汇率/跨国企业
3. 投资建议输出要求
每条建议必须包含：
机会/风险类型（政策套利/事件驱动/周期反转等）
具体标的（如黄金期货、某行业ETF、个股）
逻辑链条（使用"因A导致B进而影响C"结构）
关联新闻的标题
----------
示例输出
[机会] 贵金属短期做多机会
标的：COMEX黄金期货
逻辑链：①南非主要金矿罢工（矿业周刊）→黄金供应量预期减少4% ②美联储加息放缓信号（路透社）→美元指数走弱压力增大
操作建议：建议在1980美元/盎司支撑位建立3个月期货多头
[风险] 新能源车板块回调风险
标的：中证新能源汽车指数
逻辑链：①锂电池原材料碳酸锂库存创两年新高（财联社）→成本端支撑减弱 ②欧盟反补贴调查升级（BBC）→出口份额可能收缩
风险提示：建议减持相关ETF并设置8%止损线

请特别注意新闻中涉及[特定关注领域，如锂电池/农业供给侧]的条目，并做深度关联分析。
请用结构化排版回复，避免专业术语堆砌，保持信息密度与可读性平衡。
"""

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
    st.session_state.selectDate = st.date_input("日期", datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

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


def get_news_input_list():
    result = []
    for n_item in news_list:
        for index, row in n_item.iterrows():
            result.append(json.loads(row.drop(labels=['url']).to_json(force_ascii=False)))
    return result


submitted = st.button("🚀 新闻分析", use_container_width=True)
if submitted:
    check_llm_input()
    input_list = get_news_input_list()
    if len(input_list) <= 0:
        st.error("暂未查询到新闻数据!!!")
        st.stop()
    input_text = json.dumps(input_list, ensure_ascii=False)
    response = service.generate_response(input_text, prompt, api_key, base_url, mode_name)
    with st.status("正在分析...") as status:
        st.write_stream(response)
        status.update(
            label="分析完成", state="complete", expanded=True
        )
