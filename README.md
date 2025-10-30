CheckUpAi

CheckUpAi, is able to predict the height and weight of a user using a CNN(Convolutional Neural Network) regression model trained by me for that purpose.For all users the app gathers and creates a height,weight, and dual growth/decline graph for data visualization and uses these graphs to create a concise but informative data analysis report. For users ages 2-20 years old the app analyzes CDC(Centers for Disease Control And Prevention) growth charts to classify the most recent height and weight of the user as normal or non normal for their specified age and gender. For all users the app calculates BMI(Body Mass Index) with the most recent weight and height. For children the app uses CDC BMI charts to determine the healthiness of their BMI. For adults the app uses standard classification for BMI. Using these factors, CheckUpAi is able to come up with a final verdict on the overall healthiness of the user. 

-Detects humans in uploaded images using a YOLOv8 model

-Predicts height and weight using a CNN regression model

-Generates real-time health insights and analysis reports

-Stores and visualizes user history with charts (Matplotlib, Pandas)

-Frontend: Streamlit
-Backend: Python
-ML Models trained: YOLO(Human detection) CNN(Height And Weight Prediction)
-Libraries:OpenCV,Pandas,Matplotlib
-Database: Firebase
-Pre-Trained models used: SAM(Segment Anything Model)

NOTE:The human-detection model and the height and weight prediction model are not included to protect in this repository to protect my original work and prevent unauthorized reuse. 

