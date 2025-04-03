import streamlit as st
import random
from typing import List, Dict
import time

# ------------------ モックデータ ------------------

saunas = [
    {"id": 1, "name": "サウナ富士山", "location": "静岡県富士市", "open_hours": "10:00〜23:00", "description": "富士山が見える絶景サウナ", "image_url": "https://example.com/fuji-sauna.jpg", "entry_fee": 1200},
    {"id": 2, "name": "渋谷リラックスサウナ", "location": "東京都渋谷区", "open_hours": "24時間営業", "description": "渋谷駅徒歩5分、都会のオアシス", "image_url": "https://example.com/shibuya-sauna.jpg", "entry_fee": 1500},
    {"id": 3, "name": "札幌雪サウナ", "location": "北海道札幌市", "open_hours": "9:00〜22:00", "description": "雪景色を眺めながらととのえるサウナ", "image_url": "https://example.com/snow-sauna.jpg", "entry_fee": 1000}
]

restaurants = [
    {"id": 1, "name": "ととのい食堂", "type": "inside", "location": "施設内", "description": "サウナ後にぴったりのメニューを提供", "sauna_id": 1},
    {"id": 2, "name": "富士ラーメン", "type": "nearby", "location": "徒歩3分", "description": "ガッツリ系ラーメン店", "sauna_id": 1},
    {"id": 3, "name": "サ飯カフェ", "type": "inside", "location": "施設内2階", "description": "女性に人気のヘルシーカフェ", "sauna_id": 2},
    {"id": 4, "name": "渋谷ステーキ", "type": "nearby", "location": "徒歩5分", "description": "がっつり肉が食べたい人に", "sauna_id": 2},
    {"id": 5, "name": "雪見亭", "type": "inside", "location": "施設内", "description": "冷たい料理でととのう", "sauna_id": 3}
]

menu_items = [
    {"id": 1, "name": "冷やしトマト", "price": 300, "description": "さっぱり冷たく、ととのいの味方", "image_url": "https://example.com/tomato.jpg", "restaurant_id": 1},
    {"id": 2, "name": "塩ラーメン", "price": 800, "description": "風呂上がりの塩分補給に最高", "image_url": "https://example.com/ramen.jpg", "restaurant_id": 2},
    {"id": 3, "name": "冷製パスタ", "price": 900, "description": "暑い日でもツルッと食べられる一品", "image_url": "https://example.com/pasta.jpg", "restaurant_id": 3},
    {"id": 4, "name": "ステーキ定食", "price": 1500, "description": "サウナ後にエネルギーチャージ！", "image_url": "https://example.com/steak.jpg", "restaurant_id": 4},
    {"id": 5, "name": "冷やしそば", "price": 700, "description": "雪サウナにぴったりの冷やし系", "image_url": "https://example.com/soba.jpg", "restaurant_id": 5}
]

tags = [
    {"id": 1, "name": "さっぱり"},
    {"id": 2, "name": "ガッツリ"},
    {"id": 3, "name": "冷たい"}
]

menu_item_tags = [
    {"id": 1, "menu_item_id": 1, "tag_id": 1},
    {"id": 2, "menu_item_id": 1, "tag_id": 3},
    {"id": 3, "menu_item_id": 2, "tag_id": 2},
    {"id": 4, "menu_item_id": 3, "tag_id": 1},
    {"id": 5, "menu_item_id": 3, "tag_id": 3},
    {"id": 6, "menu_item_id": 4, "tag_id": 2},
    {"id": 7, "menu_item_id": 5, "tag_id": 1},
    {"id": 8, "menu_item_id": 5, "tag_id": 3}
]

# ------------------ ユーティリティ関数 ------------------

def get_restaurants_by_sauna(sauna_id: int) -> List[Dict]:
    return [r for r in restaurants if r["sauna_id"] == sauna_id]

def get_menu_items_by_restaurant(restaurant_id: int) -> List[Dict]:
    return [m for m in menu_items if m["restaurant_id"] == restaurant_id]

def get_tags_for_menu_item(menu_item_id: int) -> List[str]:
    tag_ids = [t["tag_id"] for t in menu_item_tags if t["menu_item_id"] == menu_item_id]
    return [t["name"] for t in tags if t["id"] in tag_ids]

def get_all_menu_items_for_sauna(sauna_id: int) -> List[Dict]:
    all_menus = []
    for rest in get_restaurants_by_sauna(sauna_id):
        all_menus.extend(get_menu_items_by_restaurant(rest["id"]))
    return all_menus

# ------------------ Streamlit UI ------------------

st.set_page_config(page_title="サ飯パスポート", layout="centered")

# CSS（暖色系 + 赤文字 + 中央揃え）
st.markdown("""
<style>
.card {
    border: 1px solid #e07a5f;
    border-radius: 12px;
    padding: 24px;
    margin: 30px 0;
    background-color: #fff3e0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    font-family: 'Arial', sans-serif;
    color: #b00020;
    text-align: center;
}
.card img {
    width: 80%;
    border-radius: 8px;
    margin: 16px auto;
}
.card h3 {
    font-size: 24px;
    margin-bottom: 12px;
    color: #b00020;
}
.card p {
    font-size: 18px;
    color: #b00020;
}
.card .tags {
    margin-top: 14px;
    font-size: 16px;
    color: #d32f2f;
}
</style>
""", unsafe_allow_html=True)

st.title("📖 サ飯パスポート")
st.caption("このアプリは非公式ファンプロジェクトです。実際の施設・価格とは異なる場合があります。")

# セッションステート初期化
if "selected_sauna_id" not in st.session_state:
    st.session_state.selected_sauna_id = None
if "selected_menus" not in st.session_state:
    st.session_state.selected_menus = []

# ガチャ画面
st.header("🎰 サウナ飯ガチャ")
sauna_names = [s["name"] for s in saunas]
selected_sauna_name = st.selectbox("🧖 サウナを選択してください：", sauna_names)
selected_sauna = next(s for s in saunas if s["name"] == selected_sauna_name)
st.session_state.selected_sauna_id = selected_sauna["id"]

if st.button("✨ ガチャを回す！ ✨"):
    with st.spinner("サ飯を選定中..."):
        time.sleep(1.5)
    candidate_menus = get_all_menu_items_for_sauna(st.session_state.selected_sauna_id)
    if candidate_menus:
        st.session_state.selected_menus = random.sample(candidate_menus, k=min(3, len(candidate_menus)))

# 結果表示（3つのカードを縦に並べて表示）
if st.session_state.selected_menus:
    st.markdown("---")
    st.header("🎉 サウナ飯ガチャ 結果！")

    for menu in st.session_state.selected_menus:
        st.markdown(f"""
        <div class="card">
            <img src="{menu['image_url']}" alt="menu image">
            <h3>🍽️ {menu['name']} - ￥{menu['price']}</h3>
            <p>{menu['description']}</p>
            <p class="tags">タグ: {'、'.join([f'#{t}' for t in get_tags_for_menu_item(menu['id'])])}</p>
        </div>
        """, unsafe_allow_html=True)

    total_food_price = sum(menu['price'] for menu in st.session_state.selected_menus)
    total_price = selected_sauna['entry_fee'] + total_food_price

    st.subheader("💰 合計金額")
    st.markdown(f"- サウナ入浴料: ￥{selected_sauna['entry_fee']}")
    st.markdown(f"- サウナ飯（3品合計）: ￥{total_food_price}")
    st.markdown(f"### 🧾 合計: ￥{total_price}")

    if st.button("🔁 もう一度ガチャを回す"):
        all_menus = get_all_menu_items_for_sauna(st.session_state.selected_sauna_id)
        st.session_state.selected_menus = random.sample(all_menus, k=min(3, len(all_menus)))
