import streamlit as st
from Class import *

todo_manager = ToDoListManager(st.session_state.username)

st.header("Tambah Tugas Baru")
task_name = st.text_input("Nama Tugas")
task_description = st.text_area("Deskripsi Tugas")
task_priority = st.selectbox("Prioritas", ["rendah", "sedang", "tinggi"])
task_deadline = st.date_input("Tanggal Deadline")
deadline_time = st.time_input("Waktu Deadline", value=None)

if st.button("Tambahkan Tugas"):
    if task_name and task_description and task_priority:
        deadline_datetime = datetime.combine(task_deadline, deadline_time)
        new_task = Task(
            name=task_name, 
            description=task_description, 
            priority=task_priority, 
            deadline=deadline_datetime, 
            username=st.session_state.username
        )
        todo_manager.add_task(new_task)
    else:
        st.warning("Harap isi semua bidang sebelum menambahkan tugas.")
