import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Trading Probability Backtest",
    layout="wide"
)

st.title("📊 Short-term Trading Probability Backtest")

ticker = st.text_input("股票代號", value="TSLA").upper()

direction = st.selectbox(
    "事件方向",
    ["當日升幅 ≥ X%", "當日跌幅 ≤ -X%"]
)

threshold = st.slider(
    "單一測試 Threshold (%)",
    min_value=1.0,
    max_value=10.0,
    value=3.0,
    step=0.1
)

st.divider()

st.subheader("成交量 Filter")

use_volume_filter = st.checkbox("啟用 Volume Filter", value=True)

volume_multiplier = st.slider(
    "當日 Volume 至少係過去20日平均 Volume 嘅幾多倍",
    min_value=0.5,
    max_value=3.0,
    value=1.2,
    step=0.1
)

file_path = f"data/{ticker}_daily.csv"


def calculate_backtest(df, threshold_value, direction_mode, volume_filter=False, volume_multi=1.2):
    temp = df.copy()

    temp["Return_%"] = temp["Close"].pct_change() * 100
    temp["Next_Return_%"] = temp["Return_%"].shift(-1)
    temp["Volume_MA20"] = temp["Volume"].rolling(20).mean()
    temp["Volume_Ratio"] = temp["Volume"] / temp["Volume_MA20"]

    if direction_mode == "當日升幅 ≥ X%":
        condition = temp["Return_%"] >= threshold_value
    else:
        condition = temp["Return_%"] <= -threshold_value

    if volume_filter:
        condition = condition & (temp["Volume_Ratio"] >= volume_multi)

    filtered = temp[condition].copy()

    if filtered.empty:
        return {
            "threshold": threshold_value,
            "sample_size": 0,
            "next_day_up_prob": None,
            "next_day_down_prob": None,
            "avg_next_return": None,
            "median_next_return": None,
            "best_next_return": None,
            "worst_next_return": None,
            "filtered": filtered
        }

    filtered["Next_Day_Up"] = filtered["Next_Return_%"] > 0
    filtered["Next_Day_Down"] = filtered["Next_Return_%"] < 0

    sample_size = len(filtered)
    next_day_up_prob = filtered["Next_Day_Up"].mean() * 100
    next_day_down_prob = filtered["Next_Day_Down"].mean() * 100
    avg_next_return = filtered["Next_Return_%"].mean()
    median_next_return = filtered["Next_Return_%"].median()
    best_next_return = filtered["Next_Return_%"].max()
    worst_next_return = filtered["Next_Return_%"].min()

    return {
        "threshold": threshold_value,
        "sample_size": sample_size,
        "next_day_up_prob": next_day_up_prob,
        "next_day_down_prob": next_day_down_prob,
        "avg_next_return": avg_next_return,
        "median_next_return": median_next_return,
        "best_next_return": best_next_return,
        "worst_next_return": worst_next_return,
        "filtered": filtered
    }


try:
    df = pd.read_csv(file_path)
    df = df.sort_values("Date").reset_index(drop=True)

    st.success(f"成功讀取 {ticker} 數據，共 {len(df)} 行")

    result = calculate_backtest(
        df=df,
        threshold_value=threshold,
        direction_mode=direction,
        volume_filter=use_volume_filter,
        volume_multi=volume_multiplier
    )

    st.subheader("單一 Threshold 測試結果")

    if result["sample_size"] == 0:
        st.warning("無符合條件嘅歷史樣本")
    else:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("樣本數", result["sample_size"])
        col2.metric("下一日上升機率", f"{result['next_day_up_prob']:.2f}%")
        col3.metric("下一日下跌機率", f"{result['next_day_down_prob']:.2f}%")
        col4.metric("下一日平均回報", f"{result['avg_next_return']:.2f}%")

        col5, col6, col7 = st.columns(3)
        col5.metric("下一日中位數回報", f"{result['median_next_return']:.2f}%")
        col6.metric("最好下一日回報", f"{result['best_next_return']:.2f}%")
        col7.metric("最差下一日回報", f"{result['worst_next_return']:.2f}%")

        st.subheader("符合條件嘅最近 30 次紀錄")
        show_cols = [
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Return_%",
            "Next_Return_%",
            "Volume_Ratio"
        ]

        st.dataframe(
            result["filtered"][show_cols].tail(30),
            use_container_width=True
        )

    st.divider()

    st.subheader("1% 至 5% Threshold 比較表")

    table_results = []

    thresholds = [x / 10 for x in range(10, 51, 5)]
    # 即係 1.0, 1.5, 2.0 ... 5.0

    for t in thresholds:
        r = calculate_backtest(
            df=df,
            threshold_value=t,
            direction_mode=direction,
            volume_filter=use_volume_filter,
            volume_multi=volume_multiplier
        )

        table_results.append({
            "Threshold (%)": t,
            "Sample Size": r["sample_size"],
            "Next Day Up Probability (%)": None if r["next_day_up_prob"] is None else round(r["next_day_up_prob"], 2),
            "Next Day Down Probability (%)": None if r["next_day_down_prob"] is None else round(r["next_day_down_prob"], 2),
            "Average Next Day Return (%)": None if r["avg_next_return"] is None else round(r["avg_next_return"], 2),
            "Median Next Day Return (%)": None if r["median_next_return"] is None else round(r["median_next_return"], 2),
            "Best Next Day Return (%)": None if r["best_next_return"] is None else round(r["best_next_return"], 2),
            "Worst Next Day Return (%)": None if r["worst_next_return"] is None else round(r["worst_next_return"], 2),
        })

    summary_df = pd.DataFrame(table_results)

    st.dataframe(summary_df, use_container_width=True)

    csv = summary_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="下載 Threshold 比較結果 CSV",
        data=csv,
        file_name=f"{ticker}_threshold_backtest_summary.csv",
        mime="text/csv"
    )

except FileNotFoundError:
    st.error(f"搵唔到 {file_path}，請確認 data folder 入面有 {ticker}_daily.csv")

except Exception as e:
    st.error(f"出錯：{e}")
