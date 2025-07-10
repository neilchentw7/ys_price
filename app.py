import streamlit as st
import pandas as pd
from pathlib import Path

# -------- 1. 載入報價檔 (CSV 版本，含容錯與欄位檢查) --------
def load_pricing_csv(uploaded_file=None):
    """讀取報價 CSV，回傳 DataFrame 與使用的檔名"""
    def read_with_fallback(path):
        encodings = ['utf-8', 'utf-8-sig', 'cp950', 'big5']
        for enc in encodings:
            try:
                df = pd.read_csv(path, encoding=enc)
                return df
            except Exception:
                continue
        st.error("❌ 無法讀取檔案，請確認是否為有效的 UTF-8 編碼 CSV。")
        st.stop()

    if uploaded_file:
        df = read_with_fallback(uploaded_file)
        return df, uploaded_file.name

    # 自動載入本地最新檔案
    here = Path(__file__).parent
    files = sorted(here.glob("新報價*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        st.error("❌ 找不到新報價*.csv 檔案，請放入資料夾或使用上傳功能")
        st.stop()

    latest_file = files[0]
    df = read_with_fallback(latest_file)
    return df, latest_file.name

# -------- 2. Streamlit 畫面 --------
st.set_page_config(page_title="載運報價查詢", layout="wide")
st.title("🚚🚧 載運米數報價查詢")

uploaded = st.file_uploader("📤 上傳新版報價（.csv）", type="csv")
df, filename = load_pricing_csv(uploaded)
st.caption(f"📄 使用報價檔案：`{filename}`")

# 檢查必要欄位是否存在
expected_cols = {"載運數量", 8, 7, 6, 5, 4, 3, 2, 1, "低米數補貼"}
if not expected_cols.issubset(set(df.columns)):
    st.error("❌ 報價檔缺少必要欄位，請確認是否包含：載運數量、8~1、低米數補貼")
    st.stop()

# -------- 3. 查詢介面 --------
keyword = st.text_input("🔍 請輸入地點關鍵字（例：宜蘭市）").strip()

if keyword:
    mask = df["載運數量"].astype(str).str.contains(keyword, case=False, na=False)
    result = df[mask].copy()

    if result.empty:
        st.warning("❌ 查無符合的地點")
    else:
        show_cols = ["載運數量", 8, 7, 6, 5, 4, 3, 2, 1, "低米數補貼"]
        result = result[show_cols]
        st.success(f"✅ 找到 {len(result)} 筆符合「{keyword}」的報價")
        st.dataframe(result.set_index("載運數量"))

        # 顯示單一筆為 JSON 方便複製參考
        if len(result) == 1:
            st.json(result.iloc[0].to_dict())

        # 提供下載
        with st.expander("⬇️ 下載查詢結果 CSV"):
            csv = result.to_csv(index=False).encode("utf-8-sig")
            st.download_button("下載結果", csv, file_name=f"{keyword}_報價.csv", mime="text/csv")
else:
    st.info("請輸入地點關鍵字以查詢對應載運報價")

# -------- 4. Footer --------
st.markdown("---")
st.markdown("📌 使用說明：將 `新報價202X.csv` 放入此資料夾，或點上方按鈕上傳報價檔。")
