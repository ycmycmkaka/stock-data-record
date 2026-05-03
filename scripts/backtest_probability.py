import pandas as pd

# ===== 可調參數 =====
FILE_PATH = "data/TSLA_daily.csv"
THRESHOLD = 3.0   # ← 你改呢度，例如 2.5 / 3 / 3.5

# ==================

df = pd.read_csv(FILE_PATH)

# 確保按時間排序
df = df.sort_values("Date").reset_index(drop=True)

# 計每日回報 %
df["Return_%"] = df["Close"].pct_change() * 100

# 計下一日回報 %
df["Next_Return_%"] = df["Return_%"].shift(-1)

# 條件：今日升 >= threshold
condition = df["Return_%"] >= THRESHOLD

filtered = df[condition].copy()

# 下一日係升（>0）
filtered["Next_Day_Up"] = filtered["Next_Return_%"] > 0

total_cases = len(filtered)
up_cases = filtered["Next_Day_Up"].sum()

if total_cases == 0:
    print("⚠️ 無符合條件數據")
else:
    probability = up_cases / total_cases * 100

    print(f"\n📊 條件：當日升幅 ≥ {THRESHOLD}%")
    print(f"樣本數：{total_cases}")
    print(f"下一日上升次數：{up_cases}")
    print(f"👉 下一日上升機率：{probability:.2f}%")

# 額外：平均下一日回報
avg_next_return = filtered["Next_Return_%"].mean()
print(f"👉 下一日平均回報：{avg_next_return:.2f}%")
