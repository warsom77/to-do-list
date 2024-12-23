import streamlit as st
import time
from Class import *
    
user_manager = UserManager()

@st.dialog("Sign Up")
def register():
    with st.form("register"):
        new_username = st.text_input("Username Baru")
        new_password = st.text_input("Password Baru", type="password")
        confirm_password = st.text_input("Konfirmasi Password", type="password")
        
        if st.form_submit_button("Sign Up", type="primary"):
            if not new_username or not new_password or not confirm_password:
                st.error("Semua kolom harus diisi!")
            elif new_password != confirm_password:
                st.error("Password tidak cocok!")
            else:
                # Simulasi proses registrasi
                success, message = user_manager.register(new_username, new_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            time.sleep(1)
            st.rerun()
            