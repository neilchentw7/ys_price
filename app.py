import streamlit as st
import pandas as pd
from pathlib import Path
import glob

# ---------- 1. 載入報價檔 ----------
@st.cache_data(show_spinner=False)
def load_pricing_xlsx(uploaded_file=None):
    """回傳 (DataFrame, 使用的檔名)"""
    if uploaded_file:                      # 使用者有上傳
        df = pd.read_excel(uploaded_file, sheet_name='工作表1')
        return df, uploaded_file.name

    # 沒上傳 → 從目前資料夾抓最新檔
    here = Path(__file__).parent
    files = sorted(here.glob("新報價*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        st.error("找不到新報價*.xlsx 檔案，請放入資料夾或使用上傳功能")
        st.stop()
    path = files[0]
    df = pd.read_excel(path, sheet_name='工作表1')
    return df, path.name

st.title("🚚🚧 載運米數報價查詢")

uploaded = st.file_uploader("上傳新版報價（.xlsx）", type="xlsx", help="若不上傳，系統自動讀取資料夾中最新的『新報價*.xlsx』")

df, filename = load_pricing_xlsx(uploaded)
st.caption(f"資料來源：{filename}")

# ---------- 2. 查詢 ----------
keyword = st.text_input("請輸入地點關鍵字（例：宜蘭市）").strip()

if keyword:
    mask = df["載運數量"].astype(str).str.contains(keyword, case=False, na=False)
    result = df.loc[mask].copy()
    if result.empty:
        st.warning("查無符合資料")
    else:
        # 只顯示 8→1 與補貼欄
        show_cols = ["載運數量", 8, 7, 6, 5, 4, 3, 2, 1, "低米數補貼"]
        st.dataframe(result[show_cols].set_index("載運數量"))

        # 若只查到一列，可額外轉 dict 顯示
        if len(result) == 1:
            st.json(result[show_cols].iloc[0].to_dict())

# ---------- 3. 延伸：年分、下載 ----------
with st.expander("下載查詢結果"):
    if keyword and not result.empty:
        csv = result.to_csv(index=False).encode("utf-8-sig")
        st.download_button("下載 CSV", csv, file_name=f"{keyword}_報價.csv", mime="text/csv")

st.markdown(
"""
---
**使用說明**  
1. 將 `app.py` 與最新的 `新報價YYYY.xlsx` 置於同一資料夾並執行 `streamlit run app.py`。  
2. 若當下沒有最新檔，可點「上傳新版報價」先行上傳。  
3. 直接輸入關鍵字（支援模糊比對）。系統會自動列出 8→1 載運米數與「低米數補貼」。  
"""
)
