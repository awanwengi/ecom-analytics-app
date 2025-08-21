
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import asyncio
from playwright.async_api import async_playwright

st.set_page_config(page_title="Ecom Analytics", layout="wide")

st.title("📊 Analisis Produk E-Commerce (Shopee + TikTok Shop)")

keyword = st.sidebar.text_input("Kata kunci produk", "gitar")
limit = st.sidebar.slider("Jumlah produk (Shopee)", 10, 100, 20, 10)
limit_tt = st.sidebar.slider("Jumlah produk (TikTok)", 5, 50, 10, 5)

# Filter tambahan
st.sidebar.markdown("### Filter Tambahan")
min_harga, max_harga = st.sidebar.slider("Rentang harga (Rp)", 0, 50000000, (0, 50000000), step=50000)
min_rating = st.sidebar.slider("Minimal rating", 0.0, 5.0, 0.0, step=0.1)

# --- Fungsi Shopee ---
def get_shopee_products(keyword, limit=20):
    url = f"https://shopee.co.id/api/v4/search/search_items?by=relevancy&keyword={keyword}&limit={limit}&newest=0&order=desc&page_type=search"
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    data = r.json()
    products = []
    for item in data.get("items", []):
        model = item["item_basic"]
        price = model["price"]/100000
        sold = model.get("sold", 0)
        rating = model.get("item_rating", {}).get("rating_star", 0)
        products.append({
            "Nama Produk": model["name"],
            "Harga (Rp)": int(price),
            "Terjual": sold,
            "Rating": rating,
            "Link": f"https://shopee.co.id/product/{model['shopid']}/{model['itemid']}"
        })
    df = pd.DataFrame(products)
    if not df.empty:
        df = df[(df["Harga (Rp)"] >= min_harga) & (df["Harga (Rp)"] <= max_harga)]
        df = df[df["Rating"] >= min_rating]
        df["GMV (Rp)"] = df["Harga (Rp)"] * df["Terjual"]
    return df

# --- Fungsi TikTok Shop (via Playwright) ---
async def get_tiktok_products(keyword, limit=10):
    products = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.tiktokglobalshop.com/search?keyword={keyword}")
        await page.wait_for_timeout(5000)
        items = await page.query_selector_all("div[data-e2e='search-card']")
        for i, item in enumerate(items[:limit]):
            try:
                title = await item.query_selector("div[data-e2e='search-card-name']")
                name = await title.inner_text() if title else "Produk"
                price_tag = await item.query_selector("span[data-e2e='search-card-price']")
                price = int(price_tag.inner_text().replace("Rp","").replace(".","")) if price_tag else 0
                sold_tag = await item.query_selector("span[data-e2e='search-card-sell-count']")
                sold_text = await sold_tag.inner_text() if sold_tag else "0"
                sold = int(''.join([c for c in sold_text if c.isdigit()])) if sold_text else 0
                products.append({
                    "Nama Produk": name,
                    "Harga (Rp)": price,
                    "Terjual (perkiraan)": sold,
                    "Link": f"https://www.tiktokglobalshop.com/search?keyword={keyword}"
                })
            except:
                continue
        await browser.close()
    df = pd.DataFrame(products)
    if not df.empty:
        df = df[(df["Harga (Rp)"] >= min_harga) & (df["Harga (Rp)"] <= max_harga)]
        df["GMV (Rp)"] = df["Harga (Rp)"] * df["Terjual (perkiraan)"]
    return df

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["🛍️ Shopee", "🛒 TikTok Shop", "📊 Perbandingan"])

with tab1:
    st.subheader("Shopee")
    if st.sidebar.button("Cari Shopee"):
        df = get_shopee_products(keyword, limit)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index("Nama Produk")["Terjual"])
        else:
            st.warning("Tidak ada data ditemukan.")

with tab2:
    st.subheader("TikTok Shop")
    if st.sidebar.button("Cari TikTok"):
        df_tt = asyncio.run(get_tiktok_products(keyword, limit_tt))
        if not df_tt.empty:
            st.dataframe(df_tt, use_container_width=True)
            st.bar_chart(df_tt.set_index("Nama Produk")["Terjual (perkiraan)"])
        else:
            st.warning("Tidak ada data ditemukan.")

with tab3:
    st.subheader("Perbandingan Shopee vs TikTok")
    if 'df' in locals() and not df.empty and 'df_tt' in locals() and not df_tt.empty:
        summary = pd.DataFrame({
            "Platform": ["Shopee", "TikTok Shop"],
            "Total Produk": [len(df), len(df_tt)],
            "Total GMV (Rp)": [df["GMV (Rp)"].sum(), df_tt["GMV (Rp)"].sum()],
            "Rata-rata Harga": [df["Harga (Rp)"].mean(), df_tt["Harga (Rp)"].mean()],
        })
        st.dataframe(summary, use_container_width=True)
        st.bar_chart(summary.set_index("Platform")["Total GMV (Rp)"])
    else:
        st.info("Jalankan pencarian di Shopee dan TikTok dulu untuk melihat perbandingan.")
