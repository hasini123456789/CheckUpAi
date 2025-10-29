import streamlit as st
import os
from pathlib import Path
import time
from backend.account_details import get_info
from backend.prepare_image import human_identify, segment_single_image, remove_background
from backend.weight_height_prediction import predict_height_weight
import numpy as np

user = st.session_state.get("user", None)
user_info = get_info(user)


st.header(f"Hello {user_info['first_name']}!")

with st.sidebar:
    st.page_link("Home.py", label="Home")
    st.page_link("pages/history_page.py", label="History")
    st.page_link("pages/checkup_page.py", label="Check Up")

keys_to_reset = [
    "front_uploaded",
    "side_uploaded",
    "front_file_path",
    "side_file_path",
    "predictions_done",
    "predictions",
    "measurement_choice",
    "start_prediction"
]

for key in keys_to_reset:
    if key in st.session_state:
        del st.session_state[key]
st.session_state.predictions_done = False
st.session_state.predictions=False
st.session_state.start_prediction=False
st.session_state.front_uploaded = False
st.session_state.side_uploaded = False

all_humans_dict={}
save_dir = "/Users/hasini/Documents/CheckUpAi/human_of_interest"
os.makedirs(save_dir, exist_ok=True)

st.subheader("Upload Front-View Image")
front_file = st.file_uploader(
    "Front view image (for height prediction):",
    type=["png", "jpg", "jpeg"],
    key="front"
    )
if front_file and not st.session_state.front_uploaded:
    front_path = os.path.join(save_dir, front_file.name)
    with open(front_path, "wb") as f:
            f.write(front_file.getbuffer())
    st.session_state.front_uploaded = True
    st.session_state.front_file_path = front_path
    st.session_state.front_file_name=front_file.name
    st.success("Front view uploaded successfully!")

st.subheader("Upload Side-View Image")
side_file = st.file_uploader(
        "Side view image (for weight prediction):",
        type=["png", "jpg", "jpeg"],
        key="side"
    )
if side_file and not st.session_state.side_uploaded:
    side_path = os.path.join(save_dir, side_file.name)
    with open(side_path, "wb") as f:
            f.write(side_file.getbuffer())
    st.session_state.side_uploaded = True
    st.session_state.side_file_path = side_path
    st.session_state.side_file_name=side_file.name
    st.success("Side view uploaded successfully!")
    
if st.button("Start Prediction"):
    st.session_state.start_prediction = True
if st.session_state.start_prediction and not st.session_state.predictions_done:
     if st.session_state.front_uploaded and st.session_state.side_uploaded:
          st.info("Processing images and predicting... Please wait...")
          all_humans_dict = {}
          front_path = st.session_state.front_file_path
          side_path = st.session_state.side_file_path

          front_humans=human_identify(front_path, save_dir)
          label_file_front = Path(os.path.join(save_dir,f"predict/labels/{st.session_state.front_file_name}")).with_suffix(".txt")
          num_people_front=0
          with open(label_file_front, "r") as f:
                for line in f.readlines():
                    line_split=line.split(" ")
                    if line_split[0]=="0":
                        num_people_front+=1

          side_humans= human_identify(side_path, save_dir)
          label_file_side = Path(os.path.join(save_dir,f"predict2/labels/{st.session_state.side_file_name}")).with_suffix(".txt")
          num_people_side=0
          with open(label_file_side, "r") as f:
                for line in f.readlines():
                    line_split=line.split(" ")
                    if line_split[0]=="0":
                        num_people_side+=1
                   
          if num_people_front>num_people_side:
                st.error("There are more people in your front view image than your side view image")
          elif num_people_front<num_people_side:
                st.error("There are more people in your side view image than your front view image")
          else:
            for i in range(num_people_front):
                mask_path_front = segment_single_image(front_path, label_file_front, save_dir, i)
                mask_path_side = segment_single_image(side_path, label_file_side, save_dir, i)
                output_name_side = f"human_side_{i}.png"
                output_path_side = os.path.join(save_dir, output_name_side)
                
                output_name_front = f"human_front_{i}.png"
                output_path_front = os.path.join(save_dir, output_name_front)
                img_side = remove_background(side_path, mask_path_side, output_path_side, (255,255,255))
                img_front = remove_background(front_path, mask_path_front, output_path_front, (255,255,255))
                
                height_pred,weight_pred=predict_height_weight(mask_path_front,mask_path_side)
                all_humans_dict[(img_side,img_front)]={"height":height_pred/30.48,"weight":weight_pred}
            st.session_state.predictions = all_humans_dict
            st.session_state.predictions_done = True
     else:
          st.error("Please upload your images!")
if st.session_state.predictions_done==True:
    st.switch_page("pages/view_results_page.py")