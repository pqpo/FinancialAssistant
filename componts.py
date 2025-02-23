import streamlit as st
import news_spider as ns
import altair as alt
import pandas as pd


def show_hang_seng_tech_index_chat():
    hang_seng_index_data = ns.hang_seng_tech_index()
    chart = alt.Chart(hang_seng_index_data).mark_line(color="red", strokeWidth=3).encode(
        x=alt.X('date:T', axis=alt.Axis(title="日期", format='%Y-%m-%d')),
        y=alt.Y('hs_index:Q', axis=alt.Axis(title="恒生科技指数"), scale=alt.Scale(domain=[3000, 7000]))
    )
    # 创建选择器（用于捕捉最近点）
    nearest = alt.selection_point(
        nearest=True,  # 捕捉最近的点
        on="mouseover",  # 鼠标悬停时触发
        fields=["date"],  # 根据日期字段匹配
        empty=False  # 确保选择器始终有值
    )
    selectors = chart.mark_point().encode(
        opacity=alt.value(0),  # 设置点为透明
    ).add_params(
        nearest  # 将选择器绑定到这些点
    )
    # 显示工具提示（tooltip）
    tooltips = chart.mark_rule(color="gray").encode(
        y="hs_index:Q",
        tooltip=[
            alt.Tooltip("date:T", title="日期"),
            alt.Tooltip("hs_index:Q", title="恒生科技指数"),
        ]
    ).transform_filter(
        nearest  # 只显示最近点的数据
    )
    layer_chart = chart + selectors + tooltips
    st.altair_chart(layer_chart, use_container_width=True)


def show_heng_shen_chat():
    hang_seng_index_data = ns.hang_seng_index()
    chart = alt.Chart(hang_seng_index_data).mark_line(color="red", strokeWidth=3).encode(
        x=alt.X('date:T', axis=alt.Axis(title="日期", format='%Y-%m-%d')),
        y=alt.Y('hs_index:Q', axis=alt.Axis(title="恒生指数"), scale=alt.Scale(domain=[14000, 28000]))
    )
    # 创建选择器（用于捕捉最近点）
    nearest = alt.selection_point(
        nearest=True,  # 捕捉最近的点
        on="mouseover",  # 鼠标悬停时触发
        fields=["date"],  # 根据日期字段匹配
        empty=False  # 确保选择器始终有值
    )
    selectors = chart.mark_point().encode(
        opacity=alt.value(0),  # 设置点为透明
    ).add_params(
        nearest  # 将选择器绑定到这些点
    )
    # 显示工具提示（tooltip）
    tooltips = chart.mark_rule(color="gray").encode(
        y="hs_index:Q",
        tooltip=[
            alt.Tooltip("date:T", title="日期"),
            alt.Tooltip("hs_index:Q", title="恒生指数"),
        ]
    ).transform_filter(
        nearest  # 只显示最近点的数据
    )
    layer_chart = chart + selectors + tooltips
    st.altair_chart(layer_chart, use_container_width=True)


def show_index_news_sentiment_scope_chat():
    news_sentiment_scope = ns.get_index_news_sentiment_scope()
    # 使用 Altair 绘制双纵坐标轴图表
    base = alt.Chart(news_sentiment_scope).encode(
        x=alt.X('日期:T', axis=alt.Axis(format='%Y-%m-%d')),
    )
    # 绘制市场情绪指数折线图
    line1 = base.mark_line(color="green", strokeWidth=3, strokeDash=[5, 5]).encode(
        y=alt.Y("市场情绪指数:Q", axis=alt.Axis(title="市场情绪指数"), scale=alt.Scale(domain=[0.8, 1.2]))
    )
    # 绘制沪深300指数折线图
    line2 = base.mark_line(color="red", strokeWidth=3).encode(
        y=alt.Y("沪深300指数:Q", axis=alt.Axis(title="沪深300指数"), scale=alt.Scale(domain=[2500, 4500]))
    )

    # 创建选择器（用于捕捉最近点）
    # nearest = alt.selection_point(
    #     nearest=True,  # 捕捉最近的点
    #     on="mouseover",  # 鼠标悬停时触发
    #     fields=["日期"],  # 根据日期字段匹配
    #     empty=False  # 确保选择器始终有值
    # )
    # # 添加透明的点（用于捕捉鼠标事件）
    # selectors = base.mark_point().encode(
    #     opacity=alt.value(0),  # 设置点为透明
    #     x="日期:T"  # 确保 x 编码与基础图表一致
    # ).add_params(
    #     nearest  # 将选择器绑定到这些点
    # )
    # # 显示工具提示（tooltip）
    # tooltips = base.mark_rule(color="gray").encode(
    #     x="日期:T",  # 确保 x 编码与基础图表一致
    #     y="市场情绪指数:Q",
    #     y2="沪深300指数:Q",
    #     tooltip=[
    #         alt.Tooltip("日期:T", title="日期"),
    #         alt.Tooltip("市场情绪指数:Q", title="市场情绪指数"),
    #         alt.Tooltip("沪深300指数:Q", title="沪深300指数")
    #     ]
    # ).transform_filter(
    #     nearest  # 只显示最近点的数据
    # )

    # 将两条折线图组合在一起
    chart = alt.layer(line1, line2,).resolve_scale(
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
    for index, row in data_frame.iterrows():
        with st.container():
            st.markdown(f"### {row['title']}")
            st.markdown(f"{row['content']}")
            left, middle, right = st.columns(3)
            with left:
                st.markdown(f"<div style='text-align: left; color: #666;'>{row['source']}（{row['category']}）</div>",
                            unsafe_allow_html=True)
            with right:
                st.markdown(f"<div style='text-align: right; color: #666;'>{row['pub_time']}</div>",
                            unsafe_allow_html=True)
            # 分隔线
            st.markdown("---")
