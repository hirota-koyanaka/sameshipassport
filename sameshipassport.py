import streamlit as st
import os
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from typing import List, Dict  # これを追加
import time
import base64
import googlemaps
## from dotenv import load_dotenv  # Removed .env loading
import pydeck as pdk
## load_dotenv()
## gmaps = googlemaps.Client(key=os.getenv("GOOGLE_API_KEY"))
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"],
    scope
)
gmaps = googlemaps.Client(key=st.secrets["env"]["GOOGLE_API_KEY"])

st.set_page_config(
    page_title="サ飯パスポート", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 認証 ---
# Using st.secrets for credentials (already set above)

# --- シートID ---
SHEET_ID = "1c1WDtrWXvDyTVis_1wzyVzkWf2Hq7SxRKuGkrdN3K4M"
 
category_icon = {
    "main": "🍽️",
    "drink": "🍺"
}


@st.cache_data
def load_sheet_as_df(sheet_id: str, sheet_name: str, _creds) -> pd.DataFrame:
    client = gspread.authorize(_creds)
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(' ', '_')
    return df

saunas_df = load_sheet_as_df(SHEET_ID, "Saunas", creds)
saunas_df = saunas_df.dropna(subset=["name"])
saunas_df = saunas_df[saunas_df["name"].str.strip() != ""]
restaurants_df = load_sheet_as_df(SHEET_ID, "Restaurants", creds)
menu_items_df = load_sheet_as_df(SHEET_ID, "Menu", creds)
tags_df = load_sheet_as_df(SHEET_ID, "MenuTags", creds)
menu_item_tags_df = load_sheet_as_df(SHEET_ID, "MenuTagRelation", creds)

saunas = saunas_df.to_dict(orient="records")
restaurants = restaurants_df.to_dict(orient="records")
menu_items = menu_items_df.to_dict(orient="records")
tags = tags_df.to_dict(orient="records")
menu_item_tags = menu_item_tags_df.to_dict(orient="records")

# ------------------ ユーティリティ関数 ------------------
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def find_nearby_good_food(lat, lng, radius=200):
    keywords = ["ラーメン", "牛丼", "カレー", "ハンバーガー"]
    found_places = []

    for keyword in keywords:
        results = gmaps.places_nearby(
            location=(lat, lng),
            radius=radius,
            keyword=keyword,
            language="ja"
        ).get("results", [])

        for place in results:
            rating = place.get("rating", 0)
            name = place.get("name")
            place_lat = place["geometry"]["location"]["lat"]
            place_lng = place["geometry"]["location"]["lng"]
            distance = haversine(lat, lng, place_lat, place_lng)
            if rating >= 3.5 and distance <= radius:
                photo_ref = None
                if "photos" in place and place["photos"]:
                    photo_ref = place["photos"][0]["photo_reference"]
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={os.getenv('GOOGLE_API_KEY')}" if photo_ref else None

                found_places.append({
                    "name": name,
                    "rating": rating,
                    "keyword": keyword,
                    "latitude": place_lat,
                    "longitude": place_lng,
                    "maps_url": f"https://www.google.com/maps/place/?q=place_id:{place['place_id']}",
                    "photo_url": photo_url
                })
    return found_places

def get_restaurants_by_sauna(sauna_id: int) -> List[Dict]:
    return [r for r in restaurants if r["sauna_id"] == sauna_id]

def get_menu_items_by_restaurant(restaurant_id: int) -> List[Dict]:
    return [m for m in menu_items if m["restaurant_id"] == restaurant_id]

def get_tags_for_menu_item(menu_item_id: int) -> List[str]:
    tag_ids = [t["tag_id"] for t in menu_item_tags if t.get("menuitemid") == menu_item_id]
    return [t["name"] for t in tags if t["id"] in tag_ids]

def get_all_menu_items_for_sauna(sauna_id: int) -> List[Dict]:
    all_menus = []
    for rest in get_restaurants_by_sauna(sauna_id):
        all_menus.extend(get_menu_items_by_restaurant(rest["id"]))
    return all_menus

def get_random_menus_by_category(menu_items: List[Dict]) -> List[Dict]:
    selected = []

    # main から1品
    mains = [item for item in menu_items if item.get('category', '').strip().lower() == 'main']
    if mains:
        selected.append(random.choice(mains))

    # drink から2品（重複しないように）
    drinks = [item for item in menu_items if item.get('category', '').strip().lower() == 'drink']
    if len(drinks) >= 2:
        selected.extend(random.sample(drinks, 2))
    elif drinks:
        selected.extend(drinks)  # 1品しかない場合はその1品だけ

    return selected

# ------------------ ユーティリティ関数: get_photo_base64 ------------------
import requests

def get_photo_base64(photo_url):
    try:
        response = requests.get(photo_url)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode()
    except Exception:
        return None
    return None

# ------------------ Streamlit UI ------------------
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
        padding: 12px 14px;
        font-size: 17px;
        line-height: 1.8;
        height: auto !important;
        overflow: visible !important;
        display: flex;
        align-items: center;
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
        st.session_state.selected_menus = get_random_menus_by_category(candidate_menus)
st.markdown('</div>', unsafe_allow_html=True)

# 結果表示
if st.session_state.selected_menus:
    lat = selected_sauna.get("latitude")
    lng = selected_sauna.get("longitude")

    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #e8d0a9; text-align: center; margin-bottom: 20px;">サ飯ガチャ 結果</h2>', unsafe_allow_html=True)

    for menu in st.session_state.selected_menus:
        icon = category_icon.get(menu.get("category", "").lower(), "🍽️")
        tags_html = ''.join([f'<span class="tag">#{t}</span>' for t in get_tags_for_menu_item(menu['id'])])
        image_path = f"images/{menu.get('image_file', '')}"
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode()
            image_html = f'<img src="data:image/jpeg;base64,{encoded}" style="width:150px; height:150px; object-fit: cover; border-radius:8px; margin-left:20px;" />'
        else:
            image_html = ""
        
        st.markdown(f"""
        <div class="result-card">
            <div style="display: flex; align-items: flex-start; justify-content: space-between;">
                <div style="flex: 1;">
                    <p class="menu-name">{icon} {menu['name']}</p>
                    <p class="price">￥{menu['price']}</p>
                    <p class="description">{menu['description']}</p>
                    <div class="tags">{tags_html}</div>
                </div>
                {image_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    raw_price = selected_sauna.get("entry_fee") or selected_sauna.get("entryfee") or selected_sauna.get("price", 0)
    try:
        sauna_fee = int(str(raw_price).replace(',', ''))
    except ValueError:
        sauna_fee = 0
    total_food_price = sum(menu['price'] for menu in st.session_state.selected_menus)
    total_price = sauna_fee + total_food_price

    st.markdown(f"""
    <div class="price-summary">
        <h3 style="color: #e8d0a9; margin-bottom: 15px;">💰 合計金額</h3>
        <p style="color: #e8d0a9; font-size: 16px;">サウナ入浴料: ￥{sauna_fee}</p>
        <p style="color: #e8d0a9; font-size: 16px;">サウナ飯（{len(st.session_state.selected_menus)}品合計）: ￥{total_food_price}</p>
        <p style="color: #e8d0a9; font-size: 20px; font-weight: bold; margin-top: 10px;">合計: ￥{total_price}</p>
    </div>
    """, unsafe_allow_html=True)

    # もう一度ボタンも中央配置
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    if st.button("もう一度ガチャを回す"):
        all_menus = get_all_menu_items_for_sauna(st.session_state.selected_sauna_id)
        st.session_state.selected_menus = get_random_menus_by_category(all_menus)
    st.markdown('</div>', unsafe_allow_html=True)
    if lat and lng:
        nearby_foods = find_nearby_good_food(lat, lng)
        if nearby_foods:
            st.markdown('<h2 style="color: #e8d0a9; text-align: center; margin-bottom: 20px;">徒歩圏内の高評価なサ飯処</h2>', unsafe_allow_html=True)
            # 地図表示
            map_data = pd.DataFrame(
                [{
                    'lat': lat,
                    'lon': lng,
                    'name': 'サウナ',
                    'type': 'サウナ',
                    'rating': None,
                    'color': [0, 128, 255]
                }] +
                [{
                    'lat': place['latitude'],
                    'lon': place['longitude'],
                    'name': place['name'],
                    'type': place['keyword'],
                    'rating': place['rating'],
                    'color': [255, 0, 80]
                } for place in nearby_foods]
            )
            map_data['rating'] = map_data['rating'].fillna(0)

            # 絵文字マッピング（ローカル画像パス）
            icon_map = {
                "サウナ": "images/pin_sauna.png",
                "カレー": "images/pin_curry.png",
                "ラーメン": "images/pin_ramen.png",
                "牛丼": "images/pin_gyudon.png",
                "ハンバーガー": "images/pin_burger.png"
            }
            
            # フォールバックアイコン（URLアイコンでも可）
            default_icon_url = "https://cdn-icons-png.flaticon.com/512/684/684908.png"
            
            # ローカル画像をbase64エンコードして使用する関数
            def get_icon_data(entry):
                icon_path = icon_map.get(entry['type'], default_icon_url)
                if os.path.exists(icon_path):
                    with open(icon_path, "rb") as f:
                        image_data = base64.b64encode(f.read()).decode()
                    return {
                        "url": f"data:image/png;base64,{image_data}",
                    "width": 40,
                    "height": 40,
                    "anchorY": 40
                    }
                else:
                    return {
                        "url": default_icon_url,
                    "width": 40,
                    "height": 40,
                    "anchorY": 40
                    }
            
            map_data["icon_data"] = map_data.apply(get_icon_data, axis=1)
            
            layer = pdk.Layer(
                "IconLayer",
                data=map_data,
                get_icon="icon_data",
                get_size=4,
                size_scale=15,
                get_position='[lon, lat]',
                pickable=True
            )

            tooltip = {
                "html": "<b>{name}</b><br>{type}<br>評価: {rating}",
                "style": {"backgroundColor": "white", "color": "black"}
            }

            view_state = pdk.ViewState(latitude=lat, longitude=lng, zoom=16)
            st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip, map_style="mapbox://styles/mapbox/light-v9"))
            emoji_map = {
                "ラーメン": "🍜",
                "カレー": "🍛",
                "牛丼": "🥩",
                "ハンバーガー": "🍔"
            }
            for store in nearby_foods:
                emoji = emoji_map.get(store['keyword'], "🍴")
                stars = "⭐" * int(round(store['rating']))
                photo_base64 = get_photo_base64(store["photo_url"]) if store.get("photo_url") else None
                if photo_base64:
                    image_html = f'<img src="data:image/jpeg;base64,{photo_base64}" style="width:150px; height:150px; object-fit: cover; border-radius:8px; margin-left:20px;" />'
                else:
                    image_html = '<div style="width:150px; height:150px; background:#444; border-radius:8px; margin-left:20px;"></div>'
                st.markdown(f"""
<div class="result-card">
    <div style="display: flex; align-items: flex-start; justify-content: space-between;">
        <div style="flex: 1;">
            <p class="menu-name">{emoji} {store['name']}（{store['keyword']}）</p>
            <p class="price">評価: {store['rating']} {stars}</p>
            <a href="{store['maps_url']}" target="_blank" style="color:#e8d0a9;">Googleマップで見る</a>
        </div>
        {image_html}
    </div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown("😢 該当エリアに評価3.5以上のお店が見つかりませんでした。", unsafe_allow_html=True)

# フッター
st.markdown("""
<div class="footer">
    <p>このサイトは、有志により開発された非公式ファンサイトです。<br>メニューは実際の取扱と異なることがあります。</p>
</div>
""", unsafe_allow_html=True)

# スタンプ風の透かし配置
st.markdown(stamp_html, unsafe_allow_html=True)