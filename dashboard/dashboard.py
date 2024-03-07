import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import date, datetime, timedelta
from babel.numbers import format_currency

# Define colors
colors = sns.color_palette("Set2", 8)

# Load data
day_df = pd.read_csv("https://raw.githubusercontent.com/fajarnyt/analisa/master/data/day.csv")
hour_df = pd.read_csv("https://raw.githubusercontent.com/fajarnyt/analisa/master/data/hour.csv")

# Merge dataframes
all_df = hour_df.merge(day_df, on='dteday', how='inner', suffixes=('_hour', '_day'))

# Define weather labels
weather_labels = {
    1: 'Cerah',
    2: 'Berkabut',
    3: 'Hujan Ringan',
    4: 'Hujan Lebat'
}
all_df['weather_label'] = all_df['weathersit_day'].map(weather_labels)

# Create a Streamlit app
st.title('Bike Sharing')

# Convert string dates to datetime.date objects
min_date = datetime.strptime('2004-01-01', '%Y-%m-%d').date()
max_date = datetime.strptime('2024-12-31', '%Y-%m-%d').date()

with st.sidebar:
    # Adding the company logo
    st.image("https://github.com/fajarnyt/gambar/blob/master/sepeda.jpg?raw=true")
    
    # Getting start_date & end_date from date_input
    date_range = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )      

########################################################################################
# Fungsi untuk menampilkan jumlah sewa sepeda berdasarkan kondisi cuaca
def visualize_bike_count_by_weather(df):
    st.write('## Jumlah sewa sepeda berdasarkan kondisi cuaca')
    avg_weather = all_df.groupby('weather_label')['cnt_day'].mean().reset_index().sort_values("cnt_day")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='weather_label', y='cnt_day', data=df, ci=None, palette='coolwarm', hatch='/')

    plt.title('Rata-rata Jumlah Sewa Sepeda Berdasarkan Kondisi Cuaca', fontsize=16)
    plt.xlabel('Kondisi Cuaca', fontsize=14)
    plt.ylabel('Jumlah Penyewa Sepeda', fontsize=14)
    plt.xticks(fontsize=12)  # Ukuran label pada sumbu x
    plt.yticks(fontsize=12)  # Ukuran label pada sumbu y
    st.pyplot(fig)
    
    # Menampilkan total keseleuruhan penyewa, total registered user, dan total casual user
    col1, col2, col3 = st.columns(3)

    with col1:
        total_customers = df['cnt_day'].sum()
        st.metric("Total Penyewa", value=total_customers)

    with col2:
        total_registered = df['registered_day'].sum()
        st.metric("Total Registered User", value=total_registered)

    with col3:
        total_casual = df['casual_day'].sum()
        st.metric("Total Casual User", value=total_casual)
#########################################################################################


#########################################################################################
#Rata-rata Jumlah Sewa Sepeda Berdasarkan Bulan
def visualize_bike_count_by_weather_workingday(df):
    st.write('## Bagimana rata-rata penyewaan sepeda untuk setiap bulan dalam setahun?')
    fig, ax = plt.subplots(figsize=(8, 6))
    
    sewa_bulan = all_df.groupby('mnth_day')['cnt_day'].mean()
    plt.step(range(len(sewa_bulan)), sewa_bulan.values, where='mid', color='black', linestyle='-', marker='o')
    plt.bar(sewa_bulan.index, sewa_bulan.values, color='#f99000', hatch='/')

    plt.title('Rata - Rata Jumlah Penyewaan Setiap Bulan', fontsize=16)
    plt.xlabel('Bulan', fontsize=14)
    plt.ylabel('Jumlah sewa Sepeda', fontsize=14)
    plt.xticks(fontsize=12)  # Ukuran label pada sumbu x
    plt.yticks(fontsize=12)  # Ukuran label pada sumbu y
    st.pyplot(fig)

def visualize_correlation_heatmap_with_windspeed(df):
    st.write('## Bagaimana rata - rata jumlah penyewaan sepeda setiap bulan dalam setahun berdasarkan kondisi cuaca cerah')
    fig, ax = plt.subplots(figsize=(8, 6))

    sewa_cerah = all_df[all_df['weather_label'] == 'Cerah'].groupby('mnth_day')['cnt_day'].mean()
    plt.step(range(len(sewa_cerah)), sewa_cerah.values, where='mid', color='black', linestyle='-', marker='o')
    plt.bar(sewa_cerah.index, sewa_cerah.values, color='red',  hatch='/')

    plt.title('Rata - Rata Penyewaan Setiap Bulan Kondisi Cuaca Cerah', fontsize=16)
    plt.xlabel('Bulan', fontsize=14)
    plt.ylabel('Jumlah sewa Sepeda', fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    return fig
############################################################################


# Fungsi untuk menampilkan visualisasi RFM
def visualize_rfm(df):
    st.write('## Visualisasi RFM (Recency, Frequency, Monetary)')
    rfm_df = df.groupby('dteday').agg({
        'dteday': lambda date: (df['dteday'].max() - date.max()).days,  # Recency
        'cnt_day': 'count',  # Frequency
        'registered_day': 'sum',  # Monetary dari pelanggan terdaftar
        'casual_day': 'sum'  # Monetary dari pelanggan non-terdaftar
    }).rename(columns={
        'dteday': 'Recency',
        'cnt_day': 'Frequency',
        'registered_day': 'Monetary_Registered',
        'casual_day': 'Monetary_Casual'
    })

    # Rata-rata RFM
    avg_recency = round(rfm_df['Recency'].mean(), 1)
    avg_frequency = round(rfm_df['Frequency'].mean(), 2)
    avg_monetary_registered = round(rfm_df['Monetary_Registered'].mean(), 2)
    avg_monetary_casual = round(rfm_df['Monetary_Casual'].mean(), 2)

    st.write(f"Average Recency (days): {avg_recency}")
    st.write(f"Average Frequency: {avg_frequency}")
    st.write(f"Average Monetary (Registered): {avg_monetary_registered}")
    st.write(f"Average Monetary (Casual): {avg_monetary_casual}")

    st.write(rfm_df.head())

    fig, ax = plt.subplots(nrows=1, ncols=4, figsize=(35, 6))  # Menambahkan 4 kolom untuk metrik rata-rata

    sns.barplot(y="Recency", x="dteday", data=rfm_df.sort_values(by="Recency", ascending=True).head(5), hue="Recency", palette='rainbow', ax=ax[0], legend=False)
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
    ax[0].tick_params(axis ='x', labelsize=10)

    sns.barplot(y="Frequency", x="dteday", data=rfm_df.sort_values(by="Frequency", ascending=False).head(5), hue="Frequency", palette='rainbow', ax=ax[1], legend=False)
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].set_title("By Frequency", loc="center", fontsize=18)
    ax[1].tick_params(axis='x', labelsize=10)

    sns.barplot(y="Monetary_Registered", x="dteday", data=rfm_df.sort_values(by="Monetary_Registered", ascending=False).head(5), hue="Monetary_Registered", palette='coolwarm', ax=ax[2], legend=False)
    ax[2].set_ylabel(None)
    ax[2].set_xlabel(None)
    ax[2].set_title("By Monetary Registered", loc="center", fontsize=18)
    ax[2].tick_params(axis='x', labelsize=10)

    # Visualisasi Monetary
    sns.barplot(y="Monetary_Casual", x="dteday", data=rfm_df.sort_values(by="Monetary_Casual", ascending=False).head(5), hue="Monetary_Casual", palette='coolwarm', ax=ax[3], legend=False)
    ax[3].set_ylabel(None)
    ax[3].set_xlabel(None)
    ax[3].set_title("By Monetary Casual", loc="center", fontsize=18)
    ax[3].tick_params(axis='x', labelsize=10)

    plt.suptitle("Best Customer Based on RFM Parameters (dteday)", fontsize=20)
    st.pyplot(fig)

def load_and_filter_data(filename, start_date, end_date):
    # Load data from file
    df = pd.read_csv(filename)

    # Convert 'dteday' column to datetime
    df['dteday'] = pd.to_datetime(df['dteday'])

    # Convert input date_range to datetime64[ns]
    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.min.time()) + timedelta(days=1)

    # Filter data based on date range input by user
    filtered_df = df[(df['dteday'] >= start_date) & (df['dteday'] < end_date)]

    return filtered_df
    
# Memuat dan menyaring data
all_df = load_and_filter_data("https://raw.githubusercontent.com/fajarnyt/analisa/master/dashboard/semua_data.csv", date_range[0], date_range[1])
# Menampilkan visualisasi
visualize_bike_count_by_weather(all_df)
visualize_bike_count_by_weather_workingday(all_df)
# Fungsi untuk menampilkan heatmap korelasi
fig = visualize_correlation_heatmap_with_windspeed(all_df)
st.pyplot(fig)
visualize_rfm(all_df)
