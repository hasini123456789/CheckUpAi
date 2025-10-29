import streamlit as st
from backend.account_details import Log_In


st.session_state["user"]=None
with st.sidebar:
    st.page_link("Home.py",label="Home")
    st.page_link("pages/login_page.py",label="Log In")
    st.page_link("pages/signup_page.py",label="Sign Up")

st.header("**Log** **In**")
username=st.text_input("Enter your username:")
password=st.text_input("Enter your password:",type="password")

st.button("Done","done_login")

if st.session_state["done_login"]:
    log_in=Log_In(username,password)
    if log_in.check_existance()==True:
        st.success("You have successfully logged in!")
        st.session_state["user"]=f"{username,password}"
        st.switch_page("pages/checkup_page.py")
    else:
        st.error("That username or password does not exist in our database! Please sign up.")
