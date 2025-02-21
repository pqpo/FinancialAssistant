import streamlit as st
import componts

st.title("📰 财经新闻助手")
st.divider()

default_prompt = "下面是最近发生的新闻，帮我总结提取一下新闻内容，通过你的阅读需要你给出判断是否会对某只或者某类股票造成影响，以及对黄金价格走势的影响。影响需要给出新闻依据。"

processResult = None

with st.sidebar:
    st.session_state.prompt = st.text_area("内容提示词", default_prompt, height=300)
    left, right = st.columns(2)
    with left:
        selection = st.pills("提取范围", ["财经", "贵金属", "CCTV"], selection_mode="multi")
        st.session_state.show_today = st.checkbox("只看今天", value=True)
    with right:
        st.container(height=55, border=False)
        if st.button("提交", use_container_width=True, icon="😃"):
            processResult = "为加大引资稳资力度，2月19日，商务部、国家发改委出台“稳外资20条”《2025年稳外资行动方案》，提出扩大电信、医疗、教育等领域开放试点，优化国家服务业扩大开放综合试点示范，鼓励外资在华开展股权投资等内容。回眸2024年，“外资准入负面清单”时隔三年后更新，制造业领域外资准入限制措施全面“清零”。商务部外国投资管理司司长朱冰此次透露，2025年有关部门将推出新版“市场准入负面清单”，进一步压减相关清单……此次“稳外资20条”应如何解读？未来有望在哪些方面进一步开放？我们可以用哪些指标来观测外资的进出去留？"
    if processResult is not None:
        st.success(processResult)

with st.expander("沪深300&市场情绪指数", expanded=False, icon="🔥"):
    componts.show_index_news_sentiment_scope_chat()

with st.container(border=True, height=500):
    finance_tab, gold_tab, cctv_tab = st.tabs(["财经", "贵金属", "CCTV"])
with finance_tab:
    componts.show_finance_news()
with gold_tab:
    componts.show_gold_news()
with cctv_tab:
    componts.show_cctv_news()
