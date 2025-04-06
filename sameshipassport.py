import streamlit as st
import random
from typing import List, Dict
import time
import base64

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

st.set_page_config(
    page_title="サ飯パスポート", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ロゴ（同フォルダ内の画像をbase64化）
with open("sameshi_logo.png", "rb") as f:
    logo_data = f.read()
logo_base64 = base64.b64encode(logo_data).decode()

# メインロゴHTML
# ↑従来のサイズ(width=150, height=150) → 1.3倍 (≈195×195)
logo_html = f'<img src="data:image/png;base64,{logo_base64}" width="195" height="195" alt="サ飯パスポートロゴ" />'

# スタンプ風の透かし用画像（例: 同じロゴを使用）
stamp_base64 = logo_base64

st.markdown(f"""
<style>
    /* 全体のベースカラーをダーク系 */
    .main {{
        background-color: #1e1e2d;
        color: #e8d0a9;
        font-family: 'Noto Sans JP', sans-serif;
        padding: 0;
        max-width: 100%;
    }}
    
    /* ヘッダー部分: 赤茶色系 */
    .passport-header {{
        background-color: #7d2a14;
        color: #e8d0a9;
        padding: 30px 20px;
        text-align: center;
        border-radius: 0;
        margin-top: -80px;
        margin-left: -80px;
        margin-right: -80px;
        position: relative;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}
    
    /* タイトル(セリフ書体) */
    .passport-title {{
        font-family: "Hiragino Mincho ProN", "Times New Roman", serif;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 20px;
        letter-spacing: 2px;
        color: #e8d0a9;
    }}
    
    /* SAMESHI PASSPORT: 枠線付き、セリフ系 */
    .passport-en-title {{
        font-family: "Times New Roman", serif;
        font-size: 20px;
        letter-spacing: 2px;
        display: inline-block;
        padding: 5px 10px;
        border: 1px solid #e8d0a9;
        margin-top: 10px;
        color: #e8d0a9;
    }}
    
    /* ロゴセンタリング */
    .centered-icon {{
        display: block;
        margin: 0 auto 20px auto;
        text-align: center;
    }}
    
    /* セレクトボックスのラベル */
    .selection-label {{
        font-size: 20px;
        margin-bottom: 10px;
        color: #e8d0a9;
    }}

    /* セレクトボックス */
    .stSelectbox > div > div {{
        background-color: #272731;
        color: #e8d0a9;
        border: 1px solid #e8d0a9;
        border-radius: 0;
        padding: 4px;
        font-size: 17px;
    }}

    /* ボタン(角丸なし、中央配置はHTML側でdiv包む) */
    .stButton > button {{
        background-color: #7d2a14 !important;
        color: #e8d0a9 !important;
        font-weight: bold;
        padding: 12px 40px;
        border-radius: 0 !important;
        border: none !important;
        font-size: 18px !important;
        margin-top: 15px;
        transition: all 0.3s;
    }}
    .stButton > button:hover {{
        background-color: #9e3418 !important;
        box-shadow: 0 0 8px rgba(158, 52, 24, 0.3);
    }}
    
    /* カード全体のスタイル */
    .result-card {{
        background-color: #272731;
        border: 1px solid #e8d0a9;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }}
    
    /* メニュー名スタイル */
    .menu-name {{
        font-size: 22px;
        font-weight: bold;
        color: #e8d0a9;
        margin-top: 10px;
    }}
    
    /* 料金スタイル */
    .price {{
        font-size: 18px;
        color: #e8d0a9;
        margin-top: 5px;
    }}
    
    /* 説明文スタイル */
    .description {{
        font-size: 16px;
        color: #e8d0a9;
        margin-top: 10px;
    }}
    
    /* タグスタイル */
    .tags {{
        margin-top: 12px;
        color: #7d2a14;
    }}
    
    .tag {{
        background-color: #e8d0a9;
        color: #7d2a14;
        padding: 5px 10px;
        border-radius: 20px;
        display: inline-block;
        margin-right: 5px;
        font-size: 14px;
        font-weight: bold;
    }}
    
    /* セパレーター */
    .separator {{
        border-top: 1px solid #e8d0a9;
        margin: 30px 0;
    }}
    
    /* フッタースタイル */
    .footer {{
        text-align: center;
        margin-top: 50px;
        color: #aaaa99;
        font-size: 14px;
    }}
    
    /* 金額表示スタイル */
    .price-summary {{
        background-color: #272731;
        border: 1px solid #e8d0a9;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
    }}
    
    /* スタンプ風透かし: */
    .stamp-watermark {{
        position: fixed;
        bottom: -100px;
        right: -100px;
        transform: rotate(-10deg);
        width: 400px;
        height: 400px;
        opacity: 0.05;
        z-index: 0;
    }}
    
    /* Made with Streamlitのフッター非表示 */
    footer {{
        visibility: hidden;
    }}
</style>
""", unsafe_allow_html=True)

# 透かし用のHTML
stamp_html = f"""
<div class="stamp-watermark">
    <img src="data:image/png;base64,{stamp_base64}" width="400" height="400" alt="スタンプ" />
</div>
"""

# ヘッダー部分
st.markdown(f"""
<div class="passport-header">
    <h1 class="passport-title">サ飯パスポート</h1>
    <div class="centered-icon">
        {logo_html}
    </div>
    <div class="passport-en-title">SAMESHI PASSPORT</div>
</div>
""", unsafe_allow_html=True)

# セッションステート初期化
if "selected_sauna_id" not in st.session_state:
    st.session_state.selected_sauna_id = None
if "selected_menus" not in st.session_state:
    st.session_state.selected_menus = []

st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
st.markdown('<p class="selection-label">サウナ施設を選ぶ</p>', unsafe_allow_html=True)

# サウナ選択
sauna_names = [s["name"] for s in saunas]
selected_sauna_name = st.selectbox("", sauna_names, label_visibility="collapsed")
selected_sauna = next(s for s in saunas if s["name"] == selected_sauna_name)
st.session_state.selected_sauna_id = selected_sauna["id"]

# ガチャを回すボタンを中央に配置
st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
if st.button("ガチャを回す"):
    with st.spinner("サ飯を選定中..."):
        time.sleep(1.5)
    candidate_menus = get_all_menu_items_for_sauna(st.session_state.selected_sauna_id)
    if candidate_menus:
        st.session_state.selected_menus = random.sample(candidate_menus, k=min(3, len(candidate_menus)))
st.markdown('</div>', unsafe_allow_html=True)

# 結果表示
if st.session_state.selected_menus:
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #e8d0a9; text-align: center; margin-bottom: 20px;">サウナ飯ガチャ 結果</h2>', unsafe_allow_html=True)

    for menu in st.session_state.selected_menus:
        tags_html = ''.join([f'<span class="tag">#{t}</span>' for t in get_tags_for_menu_item(menu['id'])])
        
        st.markdown(f"""
        <div class="result-card">
            <div style="display: flex; align-items: center;">
                <div style="flex: 1;">
                    <p class="menu-name">🍽️ {menu['name']}</p>
                    <p class="price">￥{menu['price']}</p>
                    <p class="description">{menu['description']}</p>
                    <div class="tags">{tags_html}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    total_food_price = sum(menu['price'] for menu in st.session_state.selected_menus)
    total_price = selected_sauna['entry_fee'] + total_food_price

    st.markdown(f"""
    <div class="price-summary">
        <h3 style="color: #e8d0a9; margin-bottom: 15px;">💰 合計金額</h3>
        <p style="color: #e8d0a9; font-size: 16px;">サウナ入浴料: ￥{selected_sauna['entry_fee']}</p>
        <p style="color: #e8d0a9; font-size: 16px;">サウナ飯（{len(st.session_state.selected_menus)}品合計）: ￥{total_food_price}</p>
        <p style="color: #e8d0a9; font-size: 20px; font-weight: bold; margin-top: 10px;">合計: ￥{total_price}</p>
    </div>
    """, unsafe_allow_html=True)

    # もう一度ボタンも中央配置
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    if st.button("もう一度ガチャを回す"):
        all_menus = get_all_menu_items_for_sauna(st.session_state.selected_sauna_id)
        st.session_state.selected_menus = random.sample(all_menus, k=min(3, len(all_menus)))
    st.markdown('</div>', unsafe_allow_html=True)

# フッター
st.markdown("""
<div class="footer">
    <p>このサイトについて</p>
</div>
""", unsafe_allow_html=True)

# スタンプ風の透かし配置
st.markdown(stamp_html, unsafe_allow_html=True)