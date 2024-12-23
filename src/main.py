import time
import streamlit as st
import pandas as pd
from Class import *
from forms.register import register

def main_application():
    """Main Streamlit application"""
    
    # Initialize user manager
    user_manager = UserManager()

    # Authentication state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None

    # Authentication menu
    if not st.session_state.logged_in:
        col_empty, col_main, col_empty2 = st.columns([1, 3, 1])  # Gunakan kolom untuk memusatkan form
        with col_main:
            with st.form("Sign In"):
                # Judul form
                st.title("Sign In")

                # Input fields
                username = st.text_input("", placeholder="🙍‍♂️ Username", label_visibility="collapsed")
                password = st.text_input("", placeholder="🔒 Password", type="password", label_visibility="collapsed")

                # Tombol Submit
                if st.form_submit_button("Sign In", type="primary"):
                    success, message = user_manager.login(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
                
                st.write("Don't have an account?")
                if st.form_submit_button("Sign Up", type="tertiary"):
                    register()
                    
    else:
        tambah_tugas = st.Page(
            page = "views/tambah_tugas.py",
            title = "Tambah Tugas",
            icon = ":material/add_task:",
            default = True,
        )
        
        tampilkan_tugas = st.Page(
            page = "views/tampilkan_tugas.py",
            title = "Tampilkan Tugas",
            icon = ":material/task:"
        )
        
        pg = st.navigation(pages=[tambah_tugas, tampilkan_tugas])
        pg.run()

if __name__ == "__main__":
    # Menyertakan font JetBrains Mono melalui Google Fonts
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');
            
            body {
                font-family: 'JetBrains Mono', monospace;
            }
            
            .streamlit-expanderHeader {
                font-family: 'JetBrains Mono', monospace;
            }

            .css-1d391kg {
                font-family: 'JetBrains Mono', monospace;
            }

        </style>
    """, unsafe_allow_html=True)
    main_application()