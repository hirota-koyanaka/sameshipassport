import streamlit as st
import random
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 認証 ---
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

# --- 共通読み込み関数 ---
def load_sheet_as_df(sheet_id: str, sheet_name: str, creds) -> pd.DataFrame:
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    records = sheet.get_all_records()
    return pd.DataFrame(records)

# --- スプレッドシートID ---
SHEET_ID = "1c1WDtrWXvDyTVis_1wzyVzkWf2Hq7SxRKuGkrdN3K4M"

# --- 各シートを読み込む ---
saunas_df = load_sheet_as_df(SHEET_ID, "Saunas", creds)
restaurants_df = load_sheet_as_df(SHEET_ID, "Restaurants", creds)
menu_items_df = load_sheet_as_df(SHEET_ID, "Menu", creds)
tags_df = load_sheet_as_df(SHEET_ID, "MenuTags", creds)
menu_item_tags_df = load_sheet_as_df(SHEET_ID, "MenuTagRelation", creds)

# --- カラム名を小文字に統一（安全処理） ---
for df in [saunas_df, restaurants_df, menu_items_df, tags_df, menu_item_tags_df]:
    df.columns = df.columns.astype(str).str.strip().str.lower()

# --- セッションステート初期化 ---
if "selected_sauna_id" not in st.session_state:
    st.session_state.selected_sauna_id = None
if "selected_menus" not in st.session_state:
    st.session_state.selected_menus = []

# --- CSS（カード表示） ---
st.markdown("""
<style>
.card {
    border: 2px solid #ffb703;
    border-radius: 12px;
    padding: 20px;
    margin: 20px auto;
    background-color: #fff7e6;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    width: 90%;
    max-width: 400px;
    text-align: center;
    font-family: 'Arial', sans-serif;
}
.card img {
    width: 90%;
    border-radius: 8px;
    margin-bottom: 10px;
}
.card h3 {
    margin-bottom: 10px;
    color: #d62828;
}
.card p {
    margin-bottom: 6px;
    color: #333333;
}
</style>
""", unsafe_allow_html=True)

# --- ユーティリティ関数 ---
def get_menus_by_sauna(sauna_id: int) -> pd.DataFrame:
    related_restaurants = restaurants_df[restaurants_df["sauna_id"] == sauna_id]
    rest_ids = related_restaurants["id"].tolist()
    related_menus = menu_items_df[menu_items_df["restaurant_id"].isin(rest_ids)]
    return related_menus

# --- UI開始 ---
st.title("📖 サ飯パスポート - ガチャ")

# --- サウナ選択 ---
sauna_name_list = saunas_df["name"].tolist()
selected_sauna_name = st.selectbox("🧖 サウナを選んでください", sauna_name_list)

# --- サウナID取得 & 保存 ---
selected_sauna_row = saunas_df[saunas_df["name"] == selected_sauna_name]
if not selected_sauna_row.empty:
    sauna_id = int(selected_sauna_row.iloc[0]["id"])
    st.session_state.selected_sauna_id = sauna_id

# --- ガチャを回すボタン ---
if st.button("✨ ガチャを回す！"):
    menus = get_menus_by_sauna(sauna_id)
    if not menus.empty:
        st.session_state.selected_menus = menus.sample(n=min(3, len(menus))).to_dict(orient="records")

# --- 結果表示 ---
if st.session_state.selected_menus:
    st.success("🎉 サ飯ガチャ 結果！")
    total_price = 0

    for menu in st.session_state.selected_menus:
        st.markdown(f"""
        <div class="card">
            <img src="{menu.get('image_url', '')}" alt="menu image">
            <h3>🍽️ {menu['name']} - ￥{menu['price']}</h3>
            <p>{menu['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        total_price += int(menu['price'])

    entry_fee = int(selected_sauna_row.iloc[0]["price"])
    total_price += entry_fee

    st.markdown("---")
    st.markdown(f"🧖 サウナ入浴料: ￥{entry_fee}")
    st.markdown(f"🍱 サ飯3品合計: ￥{total_price - entry_fee}")
    st.markdown(f"### 💰 合計金額: ￥{total_price}")

    # --- 再実行 / トップボタン ---
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 もう一度ガチャを回す"):
            menus = get_menus_by_sauna(st.session_state.selected_sauna_id)
            st.session_state.selected_menus = menus.sample(n=min(3, len(menus))).to_dict(orient="records")

    with col2:
        if st.button("⬅️ トップへ戻る"):
            st.session_state.selected_sauna_id = None
            st.session_state.selected_menus = []
            st.rerun()  