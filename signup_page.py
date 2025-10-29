import streamlit as st
from backend.account_details import Sign_Up

st.session_state["user"]=None
with st.sidebar:
    st.page_link("Home.py",label="Home")
    st.page_link("pages/login_page.py",label="Log In")
    st.page_link("pages/signup_page.py",label="Sign Up")

st.header("**Sign** **Up**")
first_name=st.text_input("Enter your first name:")
last_name=st.text_input("Enter your last name:")
username=st.text_input("Enter your username:")
password=st.text_input("Enter your password:")


st.button("Done","done_signup")

if st.session_state["done_signup"]:
    sign_up=Sign_Up(first_name,last_name,username,password)
    if sign_up.check_existance()==True:
        st.error("That username and password already exists! Please login if you already have an account.")
    else:
        sign_up.add_info()
        st.success("You have successfully signed in!")
        st.session_state["user"]=f"{username,password}"
        st.switch_page("pages/checkup_page.py")
       