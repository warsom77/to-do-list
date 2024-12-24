import streamlit as st
from Class import *

todo_manager = ToDoListManager(st.session_state.username)

st.title("Tambah Tugas Baru", anchor=False)
st.markdown("---")
task_name = st.text_input("Nama Tugas")
task_description = st.text_area("Deskripsi Tugas")
task_priority = st.selectbox("Prioritas", ["rendah", "sedang", "tinggi"])
task_deadline = st.date_input("Tanggal Deadline")
deadline_time = st.time_input("Waktu Deadline", value=None)

if st.button("Tambahkan Tugas", type="primary"):
    if task_name and task_description and task_priority and task_deadline and deadline_time:
        # Kombinasikan tanggal dan waktu untuk mendapatkan deadline dalam datetime
        deadline_datetime = datetime.combine(task_deadline, deadline_time)
        
        # Ambil waktu sekarang
        now = datetime.now()
        
        # Periksa apakah deadline lebih kecil dari waktu sekarang
        if deadline_datetime < now:
            st.warning("Deadline tidak boleh kurang dari waktu saat ini. Harap pilih deadline yang valid.")
        else:
            # Buat objek tugas baru jika deadline valid
            new_task = Task(
                name=task_name, 
                description=task_description, 
                priority=task_priority, 
                deadline=deadline_datetime, 
                username=st.session_state.username
            )
            todo_manager.add_task(new_task)
            st.success(f"Tugas '{task_name}' berhasil ditambahkan.")
    else:
        st.warning("Harap isi semua bidang sebelum menambahkan tugas.")
