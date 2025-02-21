import datetime

import streamlit as st
import news_spider as ns
import altair as alt
import pandas as pd


def show_index_news_sentiment_scope_chat():
    news_sentiment_scope = ns.get_index_news_sentiment_scope()
    # 使用 Altair 绘制双纵坐标轴图表
    base = alt.Chart(news_sentiment_scope.reset_index()).encode(
        x="日期:T"
    )
    # 绘制市场情绪指数折线图
    line1 = base.mark_line(color="green", strokeWidth=3, strokeDash=[5, 5]).encode(
        y=alt.Y("市场情绪指数:Q", axis=alt.Axis(title="市场情绪指数"), scale=alt.Scale(domain=[0.8, 1.2]))
    )
    # 绘制沪深300指数折线图
    line2 = base.mark_line(color="red", strokeWidth=3).encode(
        y=alt.Y("沪深300指数:Q", axis=alt.Axis(title="沪深300指数"), scale=alt.Scale(domain=[2500, 4500]))
    )
    # 将两条折线图组合在一起
    chart = alt.layer(line1, line2).resolve_scale(
        y="independent"  # 设置独立的纵坐标轴
    )
    # 显示图表
    st.altair_chart(chart, use_container_width=True)


def show_cctv_news():
    show_news(ns.get_cctv_news())


def show_gold_news():
    show_news(ns.get_gold_news())


def show_finance_news():
    stock_news_main_cx = ns.get_stock_news_main_cx()
    show_news(stock_news_main_cx)


def show_news(data_frame: pd.DataFrame):
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    for index, row in data_frame.iterrows():
        pub_time = row['pub_time'].strftime('%Y-%m-%d')
        if st.session_state.show_today:
            if pub_time != today_str:
                continue
        with st.container():
            # 使用columns布局
            col_left, col_right = st.columns([4, 1])
            with col_left:
                st.markdown(f"### {row['title']}")
                st.markdown(f"{row['content']}")
                # 显示链接（如果有）
                if row['url'] and pd.notnull(row['url']):
                    st.markdown(f"[阅读原文]({row['url']})", unsafe_allow_html=True)
            with col_right:
                st.markdown(f"<div style='text-align: right; color: #666;'>{pub_time}</div>",
                            unsafe_allow_html=True)
            # 分隔线
            st.markdown("---")
