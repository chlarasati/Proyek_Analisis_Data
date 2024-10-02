import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Mendapatkan direktori saat ini dan path untuk file CSV
current_directory = os.path.dirname(__file__)
csv_file_path = os.path.join(current_directory, 'dashboard', 'main_data.csv')

# Fungsi untuk mempersiapkan data
def prepare_data(df):
    if "order_purchase_timestamp" in df.columns:
        # Mengonversi 'order_purchase_timestamp' menjadi format datetime
        df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")
        # Membuat kolom 'purchase_month'
        df["purchase_month"] = df["order_purchase_timestamp"].dt.month
        if df["order_purchase_timestamp"].isnull().any():
            st.warning("Ada nilai yang tidak valid dalam kolom 'order_purchase_timestamp'.")
    else:
        st.error("Kolom 'order_purchase_timestamp' tidak ditemukan dalam dataset.")
    return df

# Fungsi untuk menampilkan penjualan bulanan per produk
def plot_monthly_sales(df):
    total_sales_per_product = df.groupby(["product_id", "product_category_name"])["order_item_id"].count().reset_index()
    total_sales_per_product.rename(columns={"order_item_id": "total_sales"}, inplace=True)

    top_10_products = total_sales_per_product.nlargest(10, "total_sales")["product_id"]
    monthly_trend_products = df[df["product_id"].isin(top_10_products)].groupby(["purchase_month", "product_id"])["order_item_id"].count().reset_index()
    monthly_trend_products.rename(columns={"order_item_id": "total_sales"}, inplace=True)

    plt.figure(figsize=(10, 5))
    sns.barplot(data=monthly_trend_products, x="purchase_month", y="total_sales", hue="product_id", palette="Blues_d")
    plt.title("Penjualan 10 Produk Teratas Per Bulan")
    plt.xlabel("Bulan")
    plt.ylabel("Total Penjualan")
    plt.xticks(rotation=45)
    st.pyplot(plt)

# Fungsi untuk menampilkan penjualan terbanyak per state dan bulan
def plot_best_selling_state(df):
    best_selling_state = df.groupby(["seller_state", "purchase_month", "product_category_name"]).size().reset_index(name="order_count")
    top_selling_per_state = best_selling_state.loc[best_selling_state.groupby("seller_state")["order_count"].idxmax()]
    top_selling_per_state = top_selling_per_state.sort_values(by="order_count", ascending=False)

    plt.figure(figsize=(12, 6))
    sns.barplot(data=top_selling_per_state, x="seller_state", y="order_count", palette="Blues_d")
    plt.title("Penjualan Tertinggi per State dan Bulan")
    plt.xlabel("State")
    plt.ylabel("Total Penjualan")
    plt.xticks(rotation=45)
    st.pyplot(plt)

# Fungsi untuk menampilkan distribusi skor ulasan
def plot_review_distribution(df):
    plt.figure(figsize=(10, 5))
    sns.histplot(df["review_score"], bins=5, kde=True, color="darkblue")
    plt.title("Distribusi Skor Ulasan")
    plt.xlabel("Skor Ulasan")
    plt.ylabel("Frekuensi")
    plt.grid(axis="y")
    st.pyplot(plt)

# Fungsi untuk menampilkan total penjualan per state
def plot_total_sales_by_state(df):
    total_sales_state = df.groupby("seller_state")["order_item_id"].count().reset_index()
    total_sales_state.rename(columns={"order_item_id": "total_sales"}, inplace=True)
    total_sales_state = total_sales_state.sort_values(by="total_sales", ascending=False)

    plt.figure(figsize=(10, 5))
    sns.barplot(data=total_sales_state, x="seller_state", y="total_sales", palette="Blues_d")
    plt.title("Total Penjualan per State")
    plt.xlabel("State")
    plt.ylabel("Total Penjualan")
    plt.xticks(rotation=45)
    st.pyplot(plt)

# Fungsi untuk mendapatkan 10 produk teratas
def get_top_products(df, n=10):
    total_sales_per_product = df.groupby("product_id")["order_item_id"].count().reset_index()
    total_sales_per_product.rename(columns={"order_item_id": "total_sales"}, inplace=True)
    return total_sales_per_product.nlargest(n, "total_sales")["product_id"]

# Fungsi utama
def main():
    st.title("E-Commerce Product Analysis 🏆")
    st.write("Analisis ini mencakup penjualan bulanan dari 10 produk teratas berdasarkan total penjualan.")

    # Memuat data dari file utama
    if os.path.exists(csv_file_path):
        main_data = pd.read_csv(csv_file_path)
        main_data = prepare_data(main_data)
    else:
        st.error(f"File CSV tidak ditemukan di jalur: {csv_file_path}")
        return

    # Sidebar untuk rentang waktu
    with st.sidebar:
        st.write("### Rentang Waktu Transaksi")
        if 'order_purchase_timestamp' in main_data.columns:
            min_date = main_data['order_purchase_timestamp'].min()
            max_date = main_data['order_purchase_timestamp'].max()
            start_date, end_date = st.date_input(
                label='Rentang Waktu',
                min_value=min_date,
                max_value=max_date,
                value=[min_date, max_date]
            )
        else:
            st.error("Kolom 'order_purchase_timestamp' tidak ditemukan dalam dataset.")
            return

    # Filter data berdasarkan rentang waktu
    filtered_data = main_data[(main_data['order_purchase_timestamp'] >= pd.to_datetime(start_date)) & 
                              (main_data['order_purchase_timestamp'] <= pd.to_datetime(end_date))]

    # Menampilkan penjualan terbanyak per state dan bulan
    st.write("### Penjualan Terbanyak Per State dan Bulan:")
    plot_best_selling_state(filtered_data)

    # Visualisasi distribusi skor ulasan
    st.write("### Distribusi Skor Ulasan:")
    plot_review_distribution(filtered_data)

    # Tab untuk penjualan bulanan dan tren penjualan produk teratas
    tab_monthly_sales, tab_overview, tab_trends = st.tabs(["Penjualan Bulanan", "Overview Penjualan", "Tren Penjualan Produk Teratas"])

    with tab_monthly_sales:
        selected_state = st.selectbox("Pilih State:", filtered_data['seller_state'].unique())
        st.write("### Penjualan Bulanan:")
        plot_monthly_sales(filtered_data)

    with tab_overview:
        st.write("### Total Penjualan Per State:")
        plot_total_sales_by_state(filtered_data)

    with tab_trends:
        top_products = get_top_products(filtered_data)
        selected_product = st.selectbox("Pilih Produk:", top_products)
        st.write("### Tren Penjualan per Bulan:")
        plot_monthly_sales(filtered_data)

    # Expander untuk informasi lebih lanjut
    with st.expander("Insight Visualisasi"):
        st.write(
            """Dataset ini berisi informasi tentang transaksi e-commerce yang mencakup berbagai fitur seperti kategori produk, lokasi penjual, ongkos kirim, dan ulasan.
            Analisis menunjukkan tren penjualan per bulan dan negara bagian serta kategori produk terlaris. Insight ini dapat digunakan untuk meningkatkan strategi penjualan dan logistik."""
        )

# Menjalankan aplikasi
if __name__ == "__main__":
    main()
