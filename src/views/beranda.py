import streamlit as st
import pandas as pd
from Class import *

st.title("Statistik Poin Harian", anchor=False)
user_manager = UserManager() 
# Mendapatkan data poin harian dari user_manager
points = user_manager.get_daily_points(st.session_state.username)

if all(value == 0 for value in points.values()):
    st.warning("Minggu ini belum menyelesaikan tugas. Tidak ada data poin yang tersedia untuk ditampilkan.")
else:
    # Membuat DataFrame dari data poin
    df_points = pd.DataFrame(list(points.items()), columns=['Hari', 'Poin'])
    
    # Membuat urutan hari secara manual
    order = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    
    # Mengatur kategori hari untuk mengatur urutan
    df_points['Hari'] = pd.Categorical(df_points['Hari'], categories=order, ordered=True)
    
    # Mengurutkan DataFrame berdasarkan kategori Hari
    df_points = df_points.sort_values('Hari')
    
    # Menampilkan grafik batang
    st.subheader("Grafik Poin Harian", anchor=False)
    st.line_chart(df_points.set_index('Hari'))
    
    # Membandingkan poin hari ini dengan hari kemarin
    hari_ini = order[(pd.Timestamp.now().weekday()) % 7]  # Hari ini
    hari_kemarin = order[pd.Timestamp.now().weekday() - 1]  # Hari kemarin

    # Mendapatkan poin hari ini dan hari kemarin
    poin_hari_ini = points.get(hari_ini, 0)
    poin_hari_kemarin = points.get(hari_kemarin, 0)

    # Menampilkan pesan berdasarkan perbandingan
    if poin_hari_ini > poin_hari_kemarin:
        st.success(f"Selamat! Poin Anda hari ini ({hari_ini}) lebih banyak dibandingkan hari kemarin ({hari_kemarin}). Lanjutkan kerja keras Anda! 🎉")
    elif poin_hari_ini == poin_hari_kemarin:
        st.info(f"Poin Anda hari ini ({hari_ini}) sama dengan hari kemarin ({hari_kemarin}). Pertahankan dan tingkatkan produktivitas Anda! 💪")
    else:
        st.warning(f"Poin Anda hari ini ({hari_ini}) lebih rendah dibandingkan hari kemarin ({hari_kemarin}). Ayo, selesaikan tugas untuk meningkatkan poin! 🚀")
    
    # Menampilkan data dalam tabel
    st.subheader("Tabel Poin Harian", anchor=False)
    st.table(df_points)