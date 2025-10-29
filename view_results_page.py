import streamlit as st
from backend.account_details import get_info,enter_height_weight_info
import time


with st.sidebar:
    st.page_link("Home.py", label="Home")
    st.page_link("pages/history_page.py", label="History")
    st.page_link("pages/checkup_page.py", label="Check Up")
    
user = st.session_state.get("user", None)
user_info = get_info(user)
st.header("Here are your results:")
for key,value in st.session_state.predictions.items():
        col1, col2 = st.columns([1, 2])
        with col1:
             img1=st.image(key[1],width=500)
             img2=st.image(key[0],width=500)
        with col2:
             st.subheader(f"""
                Weight:{value["weight"]:.2f} kgs Height:{value["height"]:.2f} ft
                
""")
        time_current = time.strftime("%b %d, %Y - %I:%M %p", time.localtime())
        name_options = ["+Add Name"]
        name_options+=list(user_info["history"].keys())


        selected_name = st.selectbox(
            "Please select from the given choice of names or add a name:",
            options=name_options,
        )
        
        if selected_name == "+Add Name":
                new_name = st.text_input("Type in your new name here:")
                if st.button("Save New Name", key="save_new_name"):
                    data_to_save = {
            time_current: {
            "height": float(value["height"]),
            "weight": float(value["weight"])
                }
                }
                    enter_height_weight_info(data_to_save, user, new_name)
                    st.success(f"Saved data for {new_name}")
    
        elif selected_name!="+Add Name":
                if st.button("Save to Selected Name", key="save_existing_name"):
                        data_to_save = {
                            time_current: {
                                "height":float(value["height"]),
                                "weight":float(value["weight"])
                            }
                        }
                        enter_height_weight_info(data_to_save, user,selected_name)
                        st.success(f"Updated record for {selected_name}")