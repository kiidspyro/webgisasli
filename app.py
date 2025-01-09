import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Fungsi untuk memuat data CSV
def load_data(file):
    try:
        data = pd.read_csv(file, sep=';')  # Sesuaikan separator dengan file Anda
        if 'SID_LAT' in data.columns and 'SID_LONG' in data.columns:
            data['SID_LAT'] = data['SID_LAT'].astype(str).str.replace(',', '.').astype(float)
            data['SID_LONG'] = data['SID_LONG'].astype(str).str.replace(',', '.').astype(float)
            data = data.dropna(subset=['SID_LAT', 'SID_LONG'])
        else:
            st.error("Kolom 'SID_LAT' dan 'SID_LONG' tidak ditemukan dalam file.")
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Fungsi untuk membuat peta
def create_map(data):
    if data.empty:
        st.error("Tidak ada data lokasi yang valid untuk ditampilkan di peta.")
        return None

    map_center = [data['SID_LAT'].mean(), data['SID_LONG'].mean()]
    my_map = folium.Map(location=map_center, zoom_start=6, tiles="OpenStreetMap")

    for _, row in data.iterrows():
        popup_content = f"""
        <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.4;">
            <h4>{row.get('nama', 'Tidak Ada Nama')}</h4>
            <p><strong>Jenis Spot:</strong> {row.get('jenis_spot', '-')}</p>
            <p><strong>Aksesibilitas:</strong> {row.get('aksesbilit', '-')}</p>
            <p><strong>Jenis Ikan:</strong> {row.get('jenis_ikan', '-')}</p>
            <p><strong>Latitude:</strong> {row['SID_LAT']}<br>
               <strong>Longitude:</strong> {row['SID_LONG']}<br>
               <a href="https://www.google.com/maps/dir/?api=1&destination={row['SID_LAT']},{row['SID_LONG']}" target="_blank">Lihat Rute di Google Maps</a>
            </p>
        </div>
        """
        folium.Marker(
            location=[row['SID_LAT'], row['SID_LONG']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{row.get('nama', 'Tidak Ada Nama')}"
        ).add_to(my_map)

    return my_map

# Halaman utama
def home(data=None):
    st.title('Dashboard Peta Interaktif')

    # Statistik jika ada data
    if data is not None and not data.empty:
        st.subheader("Statistik Data")
        st.write(f"**Total Lokasi:** {len(data)}")
        st.write(f"**Jenis Spot Terbanyak:** {data['jenis_spot'].mode()[0]}")
        st.write(f"**Jenis Ikan Terbanyak:** {data['jenis_ikan'].mode()[0]}")

        # Grafik pie chart
        st.subheader("Distribusi Jenis Spot")
        spot_counts = data['jenis_spot'].value_counts()
        st.bar_chart(spot_counts)

    # Panduan penggunaan
    st.subheader("Panduan Penggunaan")
    st.write("""
    1. Unggah file CSV di halaman "Peta Interaktif".
    2. Gunakan filter untuk menyesuaikan data yang ingin ditampilkan.
    3. Anda dapat menghapus lokasi yang tidak diinginkan.
    4. Unduh data yang telah diedit sesuai kebutuhan.
    """)

    # Widget cuaca (contoh statis)
    st.subheader("Informasi Cuaca")
    st.write("Cuaca di lokasi Anda saat ini: Cerah, 29°C")

# Halaman peta interaktif
def map_page():
    st.title('Peta Interaktif')

    # File uploader
    uploaded_file = st.file_uploader("Upload file CSV", type=["csv"])

    if uploaded_file is not None:
        data = load_data(uploaded_file)

        if data.empty:
            st.error("File tidak memiliki data lokasi yang valid.")
            return

        # Filter data berdasarkan field
        st.sidebar.subheader("Filter Data")
        field_filter = st.sidebar.selectbox("Filter berdasarkan field:", ["Semua"] + list(data.columns))
        if field_filter != "Semua":
            unique_values = data[field_filter].dropna().unique()
            selected_values = st.sidebar.multiselect(f"Pilih nilai untuk {field_filter}", unique_values)
            if selected_values:
                data = data[data[field_filter].isin(selected_values)]

        st.write("Data Terunggah:")
        st.dataframe(data)

        my_map = create_map(data)
        if my_map:
            folium_static(my_map, width=800, height=600)

        # Menambah data baru
        st.subheader("Tambah Data Lokasi Baru")
        with st.form("tambah_data"):
            nama = st.text_input("Nama Lokasi")
            jenis_spot = st.text_input("Jenis Spot")
            aksesibilitas = st.text_input("Aksesibilitas")
            jenis_ikan = st.text_input("Jenis Ikan")
            lat = st.number_input("Latitude", format="%.6f")
            lon = st.number_input("Longitude", format="%.6f")
            tambah_submitted = st.form_submit_button("Tambah Data")

            if tambah_submitted:
                new_row = {
                    'nama': nama, 
                    'jenis_spot': jenis_spot, 
                    'aksesbilit': aksesibilitas, 
                    'jenis_ikan': jenis_ikan, 
                    'SID_LAT': lat, 
                    'SID_LONG': lon
                }
                data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Data baru berhasil ditambahkan!")

        # Menghapus data
        st.subheader("Hapus Data Lokasi")
        with st.form("hapus_data"):
            selected_row = st.selectbox("Pilih Lokasi untuk Dihapus", data['nama'])
            delete_submitted = st.form_submit_button("Hapus")

            if delete_submitted:
                data = data[data['nama'] != selected_row]
                st.success(f"Lokasi '{selected_row}' berhasil dihapus!")

        # Fitur unduh CSV
        st.subheader("Unduh Data CSV yang Diedit")
        csv = data.to_csv(index=False, sep=';')
        st.download_button(
            label="Unduh CSV",
            data=csv,
            file_name="data_teredit.csv",
            mime="text/csv"
        )

# Fungsi utama aplikasi
def main():
    st.sidebar.title('Navigasi')
    page = st.sidebar.radio("Pilih Halaman", ["Home", "Peta Interaktif"])

    if page == "Home":
        home()
    elif page == "Peta Interaktif":
        map_page()

if __name__ == "__main__":
    main()