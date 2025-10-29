import streamlit as st

st.session_state.clear()
st.set_page_config(page_title="CheckUpAi Home")


logo_path="/Users/hasini/Documents/CheckUpAi/app_logo.png"

with st.sidebar:
    st.page_link("Home.py",label="Home")
    st.page_link("pages/login_page.py",label="Log In")
    st.page_link("pages/signup_page.py",label="Sign Up")

st.header("Welcome to CheckUpAi!")

st.write("""
CheckUpAi uses machine learning models to predict the height and weight of a human given a 
2D RGB image of the front view of the person. Results are saved and displayed. CheckUpAi
prepares the image so the model can predict with multiple people in one image.
         
The model predicts height in centimeters(cm) and weight in pounds(lbs).The height is **converted** **to** **feet** for better user understanding.

So what are you waiting for? Try it out now!:) 
         """)

st.image(logo_path,width=500)
st.write("""
The steps are super easy! 
         
**1.)** Signup or Login(shown in the sidebar)\n
         


**2.)** Navigate to the sidebar and press 'Check Up'\n
         


**3.)** Choose whether you would like to get the height,weight or both\n
         


**4.)** Image uploading! All you have to do is upload a front view and side view of the person\n


    
    
**5.)** Watch the predictions come through seamlessly !
         """)



