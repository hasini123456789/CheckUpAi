import os
import torch
from PIL import Image
from torchvision import transforms, models
import numpy as np


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
img_size = 224
model_path = "models/height_weight_estimator.pth"

mask_dir_front = "/kaggle/input/human-dataset/local-bodym/train/mask"
mask_dir_side  = "/kaggle/input/human-dataset/local-bodym/train/mask_left"



transform = transforms.Compose([
    transforms.Resize((img_size, img_size)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
])


class TwoViewRegressor(torch.nn.Module):
    def __init__(self, pretrained=True, hidden_dim=256):
        super().__init__()
        self.front_backbone = models.resnet18(pretrained=pretrained)
        self.side_backbone  = models.resnet18(pretrained=pretrained)
        self.front_backbone.fc = torch.nn.Identity()
        self.side_backbone.fc  = torch.nn.Identity()

        feat_dim = 512
        self.fc1 = torch.nn.Linear(feat_dim*2, hidden_dim)
        self.fc2 = torch.nn.Linear(hidden_dim, hidden_dim//2)
        self.out = torch.nn.Linear(hidden_dim//2, 2)
        self.dropout = torch.nn.Dropout(0.3)
        self.act = torch.nn.ReLU()

    def forward(self, front_img, side_img):
        f_feat = self.front_backbone(front_img)
        s_feat = self.side_backbone(side_img)
        x = torch.cat([f_feat, s_feat], dim=1)
        x = self.act(self.fc1(x))
        x = self.dropout(x)
        x = self.act(self.fc2(x))
        x = self.dropout(x)
        return self.out(x)

def predict_height_weight(front_mask,side_mask):
    checkpoint = torch.load(model_path, map_location=device,weights_only=False)
    target_norm = checkpoint["target_norm"]

    model = TwoViewRegressor(pretrained=False).to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()


    front_img = Image.open(front_mask).convert("RGB")
    side_img  = Image.open(side_mask).convert("RGB")

    front_tensor = transform(front_img).unsqueeze(0).to(device)  
    side_tensor  = transform(side_img).unsqueeze(0).to(device)


    with torch.no_grad():
        pred = model(front_tensor, side_tensor).cpu().numpy()[0]


    pred_un = pred * np.array(target_norm["std"]) + np.array(target_norm["mean"])
    height_pred, weight_pred = pred_un

    return height_pred,weight_pred-6.56
