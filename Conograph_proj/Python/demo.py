import streamlit as st
import plotly.express as px
import pandas as pd

# 仮のデータ
df = px.data.iris()
fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species")

# ----------- 上部メニュー風（右端） ----------------
with st.container():
    col1, col2, col3 = st.columns([7, 1, 1])
    with col1:
        st.write("")  # 空白調整
    with col2:
        file_menu = st.selectbox("ファイル", ["開く", "保存", "閉じる"], label_visibility="collapsed")
    with col3:
        run_menu = st.selectbox("実行", ["開始", "停止"], label_visibility="collapsed")
    st.selectbox("Help", ["使い方", "バージョン情報"], label_visibility="collapsed")

# ----------- 区分 1行2列 ----------------------------
st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    st.radio("区分1", ["選択A", "選択B"], horizontal=True)
with col_b:
    st.radio("区分2", ["X", "Y"], horizontal=True)

# ----------- 本体：2カラム構成 -----------------------
left, right = st.columns([1, 3])

# 左側：タグメニュー（ラジオボタンなどで）
with left:
    st.markdown("### 機能選択")
    tab_option = st.radio("モード", ["ピークサーチ", "指数付け"])

# 右側：グラフ＋テーブル
with right:
    st.markdown("### グラフ")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### データテーブル")
    st.dataframe(df, use_container_width=True)
