import streamlit as st
from Class import *

todo_manager = ToDoListManager(st.session_state.username)

st.title("Daftar Tugas", anchor=False)
st.markdown("---")
todo_manager.display_tasks()