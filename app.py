# Ecom Analytics App (app.py)
# Versi v4 dengan fitur chart visualisasi & export Excel/CSV

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Ecom Analytics App", layout="wide")

st.title("📊 E-commerce Analytics Dashboard")
st.write("Analisis produk terlaris di Shopee dan TikTok Shop")

# Sidebar menu
menu = st.sidebar.radio("Pilih Platform:", ["Shopee", "TikTok Shop"])

# Dummy data loader (bisa diganti dengan hasil scraping)
def load_dummy_data(platform):
    if platform == "Shopee":
        return pd.DataFrame({
            "Nama Produk": ["Gitar Akustik Yamaha", "Skincare Glow Up", "Earphone Gaming"],
            "Harga (Rp)": [1500000, 120000, 250000],
            "Terjual": [230, 1200, 980],
            "Rating": [4.8, 4.6, 4.7],
            "GMV (Rp)": [1500000*230, 120000*1200, 250000*980]
        })
    else:
        return pd.DataFrame({
            "Nama Produk": ["Gitar Listrik Ibanez", "Serum Wajah Whitening", "Tripod Kamera"],
            "Harga (Rp)": [3200000, 99000, 180000],
            "Terjual": [75, 3400, 640],
            "Rating": [4.9, 4.5, 4.4],
            "GMV (Rp)": [3200000*75, 99000*3400, 180000*640]
        })

# Load data
if menu == "Shopee":
    st.subheader("📦 Data Shopee")
    df = load_dummy_data("Shopee")
else:
    st.subheader("📦 Data TikTok Shop")
    df = load_dummy_data("TikTok")

st.dataframe(df)

# Download buttons
st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name=f"{menu.lower()}_data.csv", mime="text/csv")
st.download_button("⬇️ Download Excel", df.to_excel("output.xlsx", index=False), file_name=f"{menu.lower()}_data.xlsx")

# Charts
if not df.empty:
    st.subheader("📊 Visualisasi Data")

    # Bar chart - Penjualan
    fig1, ax1 = plt.subplots()
    df.sort_values("Terjual", ascending=False).head(10).plot(
        kind="bar", x="Nama Produk", y="Terjual", ax=ax1, legend=False
    )
    ax1.set_ylabel("Jumlah Terjual")
    ax1.set_title("Top Produk Berdasarkan Penjualan")
    st.pyplot(fig1)

    # Bar chart - GMV
    fig2, ax2 = plt.subplots()
    df.sort_values("GMV (Rp)", ascending=False).head(10).plot(
        kind="bar", x="Nama Produk", y="GMV (Rp)", ax=ax2, legend=False
    )
    ax2.set_ylabel("GMV (Rp)")
    ax2.set_title("Top Produk Berdasarkan GMV")
    st.pyplot(fig2)

    # Pie chart - Distribusi Rating
    fig3, ax3 = plt.subplots()
    df['Rating'].round(1).value_counts().plot(
        kind="pie", autopct='%1.1f%%', ax=ax3
    )
    ax3.set_ylabel("")
    ax3.set_title("Distribusi Rating Produk")
    st.pyplot(fig3)


# Dockerfile
st.markdown("""
### 🐳 Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
""")

# README
st.markdown("""
### 📖 README.md
```markdown
# Ecom Analytics App

Dashboard analisis produk terlaris di Shopee & TikTok Shop.

## Cara Jalankan (Local)
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Jalankan via Docker
```bash
docker build -t ecom-analytics .
docker run -p 8501:8501 ecom-analytics
```
```
""")

# requirements.txt
st.markdown("""
### 📦 requirements.txt
```text
streamlit
pandas
matplotlib
openpyxl
```
""")
