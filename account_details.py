import firebase_admin
from firebase_admin import credentials,firestore,storage,auth

cred_path="/Users/hasini/Documents/CheckUpAi/checkupai-b8967-firebase-adminsdk-fbsvc-1253ae448c.json"
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)



db=firestore.client()

class Sign_Up:
    def __init__(self,first_name,last_name,username,password):
        self.first_name=first_name
        self.last_name=last_name
        self.username=username
        self.password=password
    
    def add_info(self):
        user_ref=db.collection("users").document(f"{self.username,self.password}")
        user_ref.set({
            "first_name":self.first_name,
            "last_name":self.last_name,
            "username":self.username,
            "password":self.password,
            "history":{}
        })

    def check_existance(self):
        user_ref=db.collection("users").document(f"{self.username,self.password}")
        doc=user_ref.get()
        if doc.exists:
            return True
        else:
            return False
    



class Log_In:
    def __init__(self,username,password):
        self.username=username
        self.password=password

    def check_existance(self):
        user_ref=db.collection("users").document(f"{self.username,self.password}")
        doc=user_ref.get()
        if doc.exists:
            return True
        else:
            return False


def get_info(user):
    user_ref=db.collection("users").document(user)
    doc=user_ref.get()
    doc_dict=doc.to_dict()
    return doc_dict

def enter_height_weight_info(data,user,name):
    user_ref=db.collection("users").document(user)
    doc=user_ref.get()
    doc_dict=doc.to_dict()
    doc_dict["history"][name]=data
    user_ref.set(doc_dict,merge=True)

