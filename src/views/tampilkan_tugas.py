import streamlit as st
from Class import *

todo_manager = ToDoListManager(st.session_state.username)

st.header("Daftar Tugas")
todo_manager.display_tasks()