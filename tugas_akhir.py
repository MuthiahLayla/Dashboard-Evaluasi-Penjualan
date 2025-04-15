import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# Fungsi untuk menampilkan informasi dasar dan statistik deskriptif
def informasi_dasar(data_penjualan, sheet_name):
    df = pd.read_excel(data_penjualan, sheet_name=sheet_name)

    # Informasi dasar
    st.markdown("### 📄 Informasi Dasar")
    st.write("Data Sample:")
    st.dataframe(df.head())  
    
    # Menampilkan struktur data menggunakan buffer untuk info
    st.markdown("#### Struktur Data")
    buffer = StringIO()  # Membuat buffer untuk menampung output
    df.info(buf=buffer)  # Menyimpan info ke buffer
    st.text(buffer.getvalue())  # Menampilkan isi buffer

    # Konversi tipe data ke kategori jika kolom tersedia
    cols = ['Terdaftar di form', 'Reseller']
    if set(cols).issubset(df.columns):
        df[cols] = df[cols].astype('category')

    # Pemisah garis
    st.markdown("---")

    # Statistik deskriptif
    st.markdown("### 📊 Statistik Deskriptif")
    st.dataframe(df.describe())

    st.markdown("---")
    st.markdown("#### 📊 Distribusi Total Penjualan per Tanggal")

    df_grouped = df.groupby("Tanggal", as_index=False)["Total Penjualan"].sum()
    date_range = pd.date_range(start=df_grouped["Tanggal"].min(), end=df_grouped["Tanggal"].max())#Membuat rentang tanggal lengkap dari awal hingga akhir bulan
    df_grouped = df_grouped.set_index("Tanggal").reindex(date_range, fill_value=0).reset_index()#tanggal yang tidak ada diisi dengan 0
    df_grouped.rename(columns={"index": "Tanggal"}, inplace=True)
    # Plot grafik batang
    fig, ax = plt.subplots(figsize=(15, 7.5))
    ax.bar(df_grouped["Tanggal"], df_grouped["Total Penjualan"], color="royalblue", align="center")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.set_xticks(df_grouped["Tanggal"])
    ax.set_xticklabels(df_grouped["Tanggal"].dt.strftime("%Y-%m-%d"), rotation=45, ha="right")
    ax.set_xlabel("Tanggal")
    ax.set_ylabel("Total Penjualan")
    ax.set_title(f"Distribusi Total Penjualan per Tanggal")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig)

# Fungsi untuk analisis lanjutan
def analisis_lanjutan(data_penjualan, sheet_name, periode):
    df = pd.read_excel(data_penjualan, sheet_name=sheet_name)

    st.markdown(f"### 🔍 Analisis Lanjutan untuk {periode}")
    
    # Modus pelanggan terdaftar
    if 'Terdaftar di form' in df.columns:
        modus_terdaftar = df['Terdaftar di form'].mode()[0]  # Modus
        if modus_terdaftar == 0:
            status_pelanggan = "Mayoritas transaksi berasal dari pelanggan tidak terdaftar"
        elif modus_terdaftar == 1:
            status_pelanggan = "Mayoritas transaksi berasal dari pelanggan terdaftar"
        st.write(f"- {status_pelanggan} ({modus_terdaftar})")

    # Rata-rata transaksi per orang
    if 'ID Customer' in df.columns and 'Total Penjualan' in df.columns:
        unique_customers = df.drop_duplicates(subset=['ID Customer'])
        jumlah_customer = len(unique_customers)
        total_transaksi = df['Total Penjualan'].sum()
        rata_rata_transaksi = total_transaksi / jumlah_customer

        st.write(f"- Jumlah customer pada {periode}: {jumlah_customer}")
        st.write(f"- Total penjualan pada {periode}: {total_transaksi:,.0f}")
        st.write(f"- Rata-rata penjualan per orang pada {periode}: {rata_rata_transaksi:,.2f}")

    # Analisis transaksi reseller
    if 'Reseller' in df.columns and 'Total Penjualan' in df.columns:
        transaksi_reseller = df[df['Reseller'] == 1]['Total Penjualan']
        total_transaksi_reseller = transaksi_reseller.sum()
        jumlah_transaksi_reseller = len(transaksi_reseller)
        rata_rata_reseller = total_transaksi_reseller / jumlah_transaksi_reseller if jumlah_transaksi_reseller > 0 else 0

        st.write(f"- Total penjualan reseller pada {periode}: {total_transaksi_reseller:,.0f}")
        st.write(f"- Jumlah transaksi reseller pada {periode}: {jumlah_transaksi_reseller}")
        st.write(f"- Rata-rata penjualan reseller pada {periode}: {rata_rata_reseller:,.0f}")

    st.markdown("---")

# Fungsi untuk menghitung koefisien variasi (CV)
def calculate_cv(data_penjualan, sheet_name, column_name):
    df = pd.read_excel(data_penjualan, sheet_name=sheet_name)

    mean = np.mean(df[column_name])
    std_dev = np.std(df[column_name], ddof=0)

    if mean == 0:
        return None, "Mean is zero, CV cannot be calculated."

    cv = (std_dev / mean) * 100

    if cv < 10:
        assessment = "Variasi kecil (Data sangat homogen dan tidak banyak berubah.)"
    elif 10 <= cv <= 20:
        assessment = "Variasi sedang (Data cukup bervariasi tetapi masih dapat dianggap relatif stabil.)"
    else:
        assessment = "Variasi besar (Data memiliki fluktuasi yang tinggi dan tidak stabil.)"

    return cv, assessment

   # Fungsi untuk analisis Pareto
def pareto_analysis (data_penjualan, sheet_name, periode, jumlah_customer_tidak_terdaftar, jumlah_customer_terdaftar) :
    st.markdown('### Analisis pareto')
    df = pd.read_excel(data_penjualan, sheet_name=sheet_name)
    total_customer = int(jumlah_customer_tidak_terdaftar) + int(jumlah_customer_terdaftar)
    st.write(f"- Total Customer : {total_customer}")
    unique_customers = df.drop_duplicates(subset=['ID Customer'])
    jumlah_customer = len(unique_customers)
    presentase_customer = (jumlah_customer / total_customer) * 100
    st.write(f"- Presentase Customer yang aktif pada {periode} : {presentase_customer:.2f}% (dari total customer)")
    total_transaksi_rapih = f"{df['Total Penjualan'].sum():,}".replace(",", ".")
    st.write(f"- Yang artinya total penjualan pada {periode} : {total_transaksi_rapih} berasal dari {presentase_customer:.2f}% customer")

    # Pareto chart
    st.markdown("#### 📊 Pareto Chart (80/20)")
    st.markdown('(Grafik di bawah ini hanya menampilkan 30 top customer.)')
    if 'ID Customer' not in df.columns or 'Total Penjualan' not in df.columns:
        st.warning("Kolom 'ID Customer' atau 'Total Penjualan' tidak ditemukan di dataset.")
        return

    grouped_df = df.drop(columns=["Tanggal","Terdaftar di form", "Reseller"]).groupby('ID Customer')['Total Penjualan'].sum().reset_index()
    grouped_df = grouped_df.sort_values(by='Total Penjualan', ascending=False)
    grouped_df['Cumulative Percentage'] = grouped_df['Total Penjualan'].cumsum() / grouped_df['Total Penjualan'].sum() * 100
    grouped_df["Above 80%"] = grouped_df["Cumulative Percentage"] <= 80

    plt.rcParams.update({'font.size': 7})
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.xticks(rotation=45, ha="right")
    ax.margins(x=0.06)  # Beri ruang di sumbu X
    ax.bar(grouped_df['ID Customer'], grouped_df['Total Penjualan'], color=np.where(grouped_df["Above 80%"], "lightcoral", "skyblue"))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax2 = ax.twinx()
    ax2.plot(grouped_df['ID Customer'], grouped_df['Cumulative Percentage'], color='orange', marker='o', linestyle='-')
    ax2.axhline(80, color='red', linestyle='--', linewidth=1)
    ax2.text(len(ax.set_xlim(5, 29)) - 1, 82, "80% Threshold", color="red", fontsize=10, ha="left")

    ax.set_xlim(-1, 30)  # Hanya tampilkan 30 pelanggan pertama
    ax.set_title("Pareto Analysis : Customers Contributing to 80% of Sales")
    ax.set_xlabel("ID Customer")
    ax.set_ylabel("Total Penjualan")
    ax2.set_ylabel("Cumulative Percentage (%)")
    st.pyplot(fig)

    # Menampilkan data
    st.markdown("#### Hasil Analisis")
    top_80 = grouped_df[grouped_df['Cumulative Percentage'] <= 80]
    presentase_customer = (len(top_80) / total_customer)* 100
    st.write(f"- 80% dari total penjualan : {top_80['Total Penjualan'].sum():,.2f}")
    st.write(f"- Jumlah customer yang menyumbang 80% penjualan : {len(top_80)}")
    st.write(f"- Persentase customer yang menyumbang 80% penjualan : {presentase_customer:.2f}%")
    st.write(f"- Persentase transaksi yang menyumbang 80% penjualan : {((len(top_80) / df['Total Penjualan'].count()) * 100):.2f}%")
    st.markdown('\n')
    st.markdown('Daftar Nama customer yang menyumbang 80% penjualan :')
    #Menampilkan dataframe yang hanya berisi dengan customer yang menyumbang 80% penjualan
    df_sorted = df.groupby('ID Customer').agg({
    'Nama' : 'first',
    'Total Penjualan': 'sum',  
    }).reset_index().sort_values(by='Total Penjualan', ascending=False)
    df_sorted_rename = df_sorted.rename(columns={'Total Penjualan': 'Total Penjualan df'}) 
    top_customers = pd.merge(df_sorted_rename, grouped_df[grouped_df['Cumulative Percentage'] <= 80], on='ID Customer', how='inner')
    top_customers = top_customers.drop(columns=['Total Penjualan df'])
    st.dataframe(top_customers)



    
# Judul aplikasi Streamlit
st.title("Dashboard Evaluasi Penjualan")
st.markdown("---")
st.write(f'''
             Data penjualan harus terdiri dari kolom : 
             - Tanggal
             - ID Customer
             - Nama
             - Terdaftar di form (memiliki 2 nilai : 0 & 1 )
             - Reseller (memiliki 2 nilai : 0 & 1 )
             - Total Penjualan
             ''')
st.write(f'''
             Data Pelanggan harus memiliki kolom : 
             - id customer
             ''')
st.text('Nama kolom harus sama persis seperti di atas.')
st.markdown("---")
pilihan = st.selectbox('Apa yang ingin Anda lakukan?',['📊 Analisis Data Penjualan','🔍 Analisis Perilaku Pelanggan', '👥 Segmentasi RFM'])

#Analisis Data Penjualan
if pilihan == '📊 Analisis Data Penjualan' :
    st.subheader("📊 Analisis Data Penjualan")
    st.markdown('''
    Analisis Data Penjualan Terdiri dari:
    1. Informasi Dasar:
       - Menampilkan 5 baris pertama data dan struktur kolom beserta tipe datanya.
       - Menyediakan statistik deskriptif untuk kolom numerik.
       - Menampilkan grafik distribusi total penjualan per tanggal.
    2. Analisis Lanjutan:
       - Status Pelanggan: Mengidentifikasi apakah transaksi berasal dari pelanggan terdaftar atau tidak terdaftar.
       - Rata-Rata Transaksi per Pelanggan: Menghitung rata-rata jumlah transaksi per pelanggan.
       - Analisis Reseller: Mengevaluasi transaksi yang dilakukan oleh reseller, termasuk total penjualan dan rata-rata transaksi.
    3. Koefisien Variasi (CV):
       - Mengukur tingkat variasi dalam penjualan menggunakan Koefisien Variasi, untuk menilai seberapa stabil performa penjualan dari waktu ke waktu.
    4. Analisis Pareto
    ''')
    st.markdown("---")
    uploaded_file = st.file_uploader("**Silahkan unggah file excel di bawah ini 📥 :**", type=["xlsx"])
    # Jika file di-upload
    if uploaded_file:
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        sheet_name = st.selectbox("Pilih Sheet:", sheet_names, index=0)
    

        st.markdown("---")
        informasi_dasar(uploaded_file, sheet_name) # informasi dasar
        # Menjalankan analisis lanjutan
        periode = st.text_input("Masukkan periode analisis (contoh: Januari 2024):", "Januari 2024")
        if st.button("Jalankan Analisis Lanjutan"):
             analisis_lanjutan(uploaded_file, sheet_name, periode)

        # Menjalankan fitur CV
        st.markdown("### 📉 Koefisien Variasi (CV)")
        column_name = st.selectbox("Pilih Kolom untuk Analisis CV:", pd.read_excel(uploaded_file, sheet_name=sheet_name).columns)
        if st.button("Hitung CV"):
            cv, assessment = calculate_cv(uploaded_file, sheet_name, column_name)
            if cv is not None:
                st.success(f"Koefisien Variasi: {cv:.2f}%")
                st.info(assessment)
            else:
                st.error(assessment)
        st.markdown("---")

        jumlah_customer_tidak_terdaftar = st.text_input("Masukkan jumlah customer tidak terdaftar", "117")
        jumlah_customer_terdaftar = st.text_input("Masukkan jumlah customer terdaftar", "177")
        if st.button('Jalankan analisis Pareto') :
            pareto_analysis (uploaded_file, sheet_name, periode, jumlah_customer_tidak_terdaftar, jumlah_customer_terdaftar)

if pilihan == '🔍 Analisis Perilaku Pelanggan' :
    st.subheader("🔍 Analisis Perilaku Pelanggan")
    st.markdown("---")
    st.markdown('''
                Analisis Perilaku Pelanggan terdiri dari :
                - Analisis Frekuensi Transaksi Pelanggan
                - Identifikasi Pelanggan Terdaftar yang Tidak Bertransaksi
                - Visualisasi Distribusi Pelanggan Aktif vs Tidak Aktif
    ''')
    uploaded_file_sales = st.file_uploader("Unggah data penjualan ke sini :", type=["xlsx"])
    uploaded_file_member = st.file_uploader("Unggah data member ke sini :", type=["xlsx"])
    st.markdown("---")
    
    if uploaded_file_sales and uploaded_file_member :
        pelanggan_terdaftar_di_form = pd.ExcelFile(uploaded_file_member)
        sheet_names1 = pelanggan_terdaftar_di_form.sheet_names
        st.markdown("**🔴 Pilih Sheet data member:**")
        sheet_name1 = st.selectbox("", sheet_names1, index=0)
        pelanggan_data = pd.read_excel(pelanggan_terdaftar_di_form, sheet_name=sheet_name1)
        if uploaded_file_sales :
            xls = pd.ExcelFile(uploaded_file_sales)
            sheet_names = xls.sheet_names
            st.markdown("**🔴 Pilih sheet data penjualan yang ingin diproses:**")
            selected_sheets = st.multiselect("", sheet_names)
            if len(selected_sheets) >= 1:
                data_frames = {}
                for sheet in selected_sheets:
                    data_frames[sheet] = pd.read_excel(xls, sheet_name=sheet)
                for sheet, df in data_frames.items():
                    df["Bulan"] = sheet
                sales_data = pd.concat(data_frames.values(), ignore_index=True)
        pelanggan_data.rename(columns={"id customer": "ID Customer"}, inplace=True)
        #untuk memastikan kolom yang dibutuhkan ada
        required_columns_sales = {"ID Customer", "Terdaftar di form"}
        required_columns_customers = {"ID Customer"}
        st.markdown("---")
        if required_columns_sales.issubset(sales_data.columns) and required_columns_customers.issubset(pelanggan_data.columns):
            # Analisis transaksi per bulan
            transactions_per_month = sales_data.groupby(["Bulan", "ID Customer"]).size().reset_index(name="Jumlah Transaksi")
            st.subheader("Kategori Frekuensi Transaksi Pelanggan per Bulan")
            st.write(f'''
                     ditentukan berdasarkan kuartil jumlah transaksi setiap bulan :
                        - Jarang : ≤ Q1. 
                        - Biasa : antara Q1 dan Q3.
                        - Sering : > Q3
                     ''')
            st.markdown('📌 Q1 & Q3 dihitung per bulan, jadi batas setiap kategori bisa beda setiap bulannya.')
            #Mengkategorikan
            data_per_pelanggan = []
            kuartil_list = []
            for bulan in transactions_per_month['Bulan'].unique(): # .unique() ngambil daftar semua bulan yang muncul, tapi TANPA duplikat
                df_bulan = transactions_per_month[transactions_per_month['Bulan'] == bulan].copy() # Mengambil semua baris yang bulannya sama dengan bulan
                # Hitung kuartil untuk kategorisasi
                q1 = df_bulan['Jumlah Transaksi'].quantile(0.25)
                q3 = df_bulan['Jumlah Transaksi'].quantile(0.75)
                kuartil_list.append({'Bulan': bulan, 'Q1': q1, 'Q3': q3})
                def kategorikan(x):
                    if x <= q1:
                        return 'Jarang'
                    elif x <= q3:
                        return 'Biasa'
                    else:
                        return 'Sering'
                df_bulan['Kategori'] = df_bulan['Jumlah Transaksi'].apply(kategorikan)
                # Buat kolom Kategori jadi urutan tetap
                kategori_order = pd.CategoricalDtype(['Sering', 'Biasa', 'Jarang'], ordered=True)
                df_bulan['Kategori'] = df_bulan['Kategori'].astype(kategori_order)
                data_per_pelanggan.append(df_bulan)
            hasil_kategori_per_pelanggan = pd.concat(data_per_pelanggan, ignore_index=True)
            hasil_kategori_per_pelanggan = hasil_kategori_per_pelanggan.sort_values(by=['Bulan', 'Kategori'])
            df_kuartil = pd.DataFrame(kuartil_list)
            st.dataframe(df_kuartil)
            st.dataframe(hasil_kategori_per_pelanggan)
            # Grafik Bar Chart
            st.markdown("Grafik Jumlah Pelanggan Berdasarkan Kategori Frekuensi Transaksi Tiap Bulan")
            # Hitung jumlah pelanggan per kategori tiap bulan
            kategori_df = (hasil_kategori_per_pelanggan.groupby(['Bulan', 'Kategori'], observed=True).size()
                           .unstack(fill_value=0).reindex(columns=['Sering', 'Biasa', 'Jarang'])# urutan kategorinya
                           )
            # Plot
            ax = kategori_df.plot( kind='bar', stacked=True, color=['#4CAF50', '#FFC107', '#F44336'],  # hijau, kuning, merah  
                                  figsize=(10, 6))
            # Menambahkan label angka di tengah batang
            for p in ax.patches:
                if p.get_height() > 0:ax.annotate(str(int(p.get_height())),
                                                   (p.get_x() + p.get_width() / 2, p.get_y() + p.get_height() / 2),
                                                     ha='center', va='center', fontsize=10, color='black')
            plt.title("Jumlah Pelanggan Berdasarkan Kategori Frekuensi Transaksi Tiap Bulan", fontsize=14, fontweight='bold')
            plt.xlabel("Bulan")
            plt.ylabel("Jumlah Pelanggan")
            plt.legend(title="Kategori")
            plt.tight_layout()
            st.pyplot(plt)

            st.markdown("---")
            # Identifikasi pelanggan terdaftar yang tidak bertransaksi
            sales_data_registered = sales_data[sales_data["Terdaftar di form"] == 1].copy()
            total_transactions_registered= sales_data_registered.groupby("ID Customer").size().reset_index(name="Total Transaksi")
            pelanggan_data["Bertransaksi"] = pelanggan_data["ID Customer"].isin(total_transactions_registered["ID Customer"])
            no_transactions = pelanggan_data[~pelanggan_data["Bertransaksi"]]
            st.subheader("Pelanggan Terdaftar yang Tidak Bertransaksi")
            st.dataframe(no_transactions)
            no_transactions_count = no_transactions['ID Customer'].count()
            st.write(f'Jumlah Pelanggan yang Tidak Bertranaksi = {no_transactions_count}')
            # Ambil input dan ubah ke integer
            jumlah_customer_tidak_terdaftar = int(st.text_input("Masukkan jumlah customer tidak terdaftar", "47"))
            jumlah_customer_terdaftar = int(st.text_input("Masukkan jumlah customer terdaftar", "177"))
            total_pelanggan = jumlah_customer_tidak_terdaftar + jumlah_customer_terdaftar
            st.write(f'Total Pelanggan : {total_pelanggan}')

            jumlah_pelanggan_aktif = total_pelanggan - no_transactions_count
            st.write(f'Jumlah Pelanggan Aktif : {jumlah_pelanggan_aktif}')
            #pie chart
            # memasukkan ke dalam Series atau list
            kategori_counts = pd.Series({'Pelanggann Terdaftar yang Tidak Bertransaksi': no_transactions_count,'Pelanggan yang Bertransaksi (Terdaftar & Tidak Terdaftar)': jumlah_pelanggan_aktif})
            custom_colors = ['#ff6666', '#66b3ff']  # merah, biru
            plt.figure(figsize=(10, 6))
            wedges, texts, autotexts = plt.pie(kategori_counts, labels=kategori_counts.index, 
                                               autopct='%1.1f%%', startangle=140, colors=custom_colors, 
                                               textprops={'fontsize': 12}, wedgeprops={'edgecolor': 'black'})
            plt.title("Distribusi Pelanggan Terdaftar yang Tidak Bertransaksi", fontsize=14, fontweight='bold', pad=20)
            plt.axis('equal')  # u/Menjaga proporsi lingkaran
            st.pyplot(plt)




        else:
         st.error("Format tidak sesuai. Pastikan kolom 'ID Customer' dan 'Terdaftar di form' ada di data penjualan, serta 'id customer' di data member.")

if pilihan == '👥 Segmentasi RFM' :
    import datetime as dt
    st.subheader("👥 Segmentasi RFM")
    st.markdown("---")
    uploaded_file_sales = st.file_uploader("Unggah data penjualan ke sini :", type=["xlsx"])
    uploaded_file_member = st.file_uploader("Unggah data member ke sini :", type=["xlsx"])
    if uploaded_file_sales and uploaded_file_member :
        pelanggan_terdaftar_di_form = pd.ExcelFile(uploaded_file_member)
        sheet_names1 = pelanggan_terdaftar_di_form.sheet_names
        st.markdown("**🔴 Pilih Sheet data member:**")
        sheet_name1 = st.selectbox("", sheet_names1, index=0)
        pelanggan_data = pd.read_excel(pelanggan_terdaftar_di_form, sheet_name=sheet_name1)
        if uploaded_file_sales :
            xls = pd.ExcelFile(uploaded_file_sales)
            sheet_names = xls.sheet_names
            st.markdown("**🔴 Pilih sheet data penjualan yang ingin diproses:**")
            selected_sheets = st.multiselect("", sheet_names)
            if len(selected_sheets) >= 1:
                data_frames = {}
                for sheet in selected_sheets:
                    data_frames[sheet] = pd.read_excel(xls, sheet_name=sheet, parse_dates=['Tanggal'])
                for sheet, df in data_frames.items():
                    df["Bulan"] = sheet
                sales_data = pd.concat(data_frames.values(), ignore_index=True)
                #untuk memastikan kolom yang dibutuhkan ada
                required_columns_sales = {"ID Customer", "Terdaftar di form"}
                required_columns_customers = {"id customer"}
                if required_columns_sales.issubset(sales_data.columns) and required_columns_customers.issubset(pelanggan_data.columns):
                    snapshot_date = st.date_input("Pilih Tanggal Snapshot", dt.date(2024, 12, 31))
                    snapshot_date = dt.datetime.combine(snapshot_date, dt.datetime.min.time())
                    rfm = sales_data.groupby('ID Customer').agg({
                        'Nama': 'first',
                        'Tanggal': lambda x: (snapshot_date - x.max()).days,  # Recency
                        'ID Customer': 'count',  # Frequency
                        'Total Penjualan': 'sum',  # Monetary
                        'Terdaftar di form': 'first',
                        'Reseller': 'first'})
                    rfm.rename(columns={
                        'Tanggal': 'Recency',
                        'ID Customer': 'Frequency',
                        'Total Penjualan': 'Monetary'}, inplace=True)
                    def get_rfm_score(recency, frequency, monetary):
                        r_score = 3 if recency <= 30 else 2 if 31 <= recency <= 59 else 1
                        f_score = 4 if frequency >= 12 else 3 if 6 <= frequency <= 12 else 2 if 3 <= frequency <= 5 else 1
                        m_score = 4 if monetary > 500000 else 3 if 300000 <= monetary <= 500000 else 2 if 100000 <= monetary <= 299000 else 1
                        return r_score, f_score, m_score
                    rfm[['R', 'F', 'M']] = rfm.apply(lambda row: pd.Series(get_rfm_score(row['Recency'], row['Frequency'], row['Monetary'])), axis=1)
                    # Fungsi untuk Kategorisasi
                    def categorize_customer(r, f, m):
                        if r == 3 and f == 4 and m == 4:
                            return "Best Customers"
                        elif r == 3 and (f in [3, 4]) and (m in [3, 4]):
                            return "Loyal Customers"
                        elif r == 3 and (f in [3, 4]) and (m in [1, 2]):
                            return "Budget Buyers"
                        elif r in [1, 2] and f in [1, 2] and m in [2, 3]:
                            return "Churn Risk"
                        elif r == 1 and f == 1 and m == 1:
                            return "Lost Customers"
                        elif r in [1, 2, 3] and f in [1, 2] and m == 4:
                            return "Big Spenders"
                        elif r == 3 and f in [1, 2] and m in [2, 3, 4]:
                            return "Potential Customers"
                        else:
                            return "OTHER"
                    rfm["Kategori"] = rfm.apply(lambda row: categorize_customer(row["R"], row["F"], row["M"]), axis=1)
                    st.subheader("Hasil RFM Analysis")
                    categories = {
                        "Best Customers": rfm[rfm["Kategori"] == "Best Customers"],
                        "Loyal Customers": rfm[rfm["Kategori"] == "Loyal Customers"],
                        "Budget Buyers": rfm[rfm["Kategori"] == "Budget Buyers"],
                        "Churn Risk": rfm[rfm["Kategori"] == "Churn Risk"],
                        "Lost Customers": rfm[rfm["Kategori"] == "Lost Customers"],
                        "Big Spenders": rfm[rfm["Kategori"] == "Big Spenders"],
                        "Potential Customers": rfm[rfm["Kategori"] == "Potential Customers"],
                        "OTHER": rfm[rfm["Kategori"] == "OTHER"]}
                    # Menampilkan jumlah pelanggan dalam setiap kategori
                    st.subheader("• Jumlah pelanggan dalam setiap kategori :")
                    kategori_counts = rfm["Kategori"].value_counts()
                    st.write(kategori_counts)
                    st.markdown("---")

                    plt.figure(figsize=(10, 6))
                    colors = plt.cm.Set3.colors  # Warna pastel
                    wedges, texts, autotexts = plt.pie( kategori_counts, labels=kategori_counts.index, autopct='%1.1f%%',
                                                        startangle=140, colors=colors, textprops={'fontsize': 12}, wedgeprops={'edgecolor': 'black'})
                    plt.title("Distribusi Pelanggan Berdasarkan Kategori RFM", fontsize=14, fontweight='bold', pad=20)
                    plt.axis('equal')  # Menjaga proporsi lingkaran
                    st.pyplot(plt)
                    st.markdown("---")

                    # Menampilkan DataFrame masing-masing kategori
                    for category, data in categories.items():
                        st.subheader(f"{category}")
                        st.dataframe(data)
                    
            
                    
            
            

    
    
    
            
    
            
    
    

        
    
    


        
        
        


  



        
            


    
