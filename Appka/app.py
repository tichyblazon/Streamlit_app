import streamlit as st

#Navigacia medzi strankami
pg = st.navigation([st.Page("app_pages/home_page.py", title = "Domov"),
                    st.Page("app_pages/predikcia_page.py", title = "Predikcia")], position="top")
pg.run()

#py -m streamlit run app.py
