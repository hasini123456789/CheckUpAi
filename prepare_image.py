import os
import cv2
import numpy as np
from segment_anything import sam_model_registry, SamPredictor
from ultralytics import YOLO

object_indentification_model="/Users/hasini/Documents/CheckUpAi/models/human_identification.pt"
sam_path="/Users/hasini/Documents/CheckUpAi/models/sam_vit_h_4b8939.pth"
model = YOLO()

def human_identify(image_path,folder):
   model.predict(
        conf=0.8,
        source=image_path,
        save=True,
        save_txt=True,
        project=folder)

    




def segment_single_image(
    image_path,
    label_path,
    folder,
    line_to_segment, 
    checkpoint_path=sam_path,
    model_type="vit_h",
  
):

    sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
    sam.to("cpu")  
    predictor = SamPredictor(sam)

    os.makedirs(folder, exist_ok=True)

   
    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        raise ValueError(f"Image not found: {image_path}")
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    h, w, _ = image_rgb.shape
    predictor.set_image(image_rgb)

 
    if not os.path.exists(label_path):
        raise ValueError(f"Label file not found: {label_path}")
    with open(label_path, "r") as f:
        lines = f.readlines()

 
    if line_to_segment < 0 or line_to_segment >= len(lines):
        raise IndexError(f"line_to_segment {line_to_segment} out of range. File has {len(lines)} lines.")


    def yolo_to_xyxy(box, img_w, img_h):
        x_c, y_c, bw, bh = box
        x_c *= img_w
        y_c *= img_h
        bw *= img_w
        bh *= img_h
        x_min = int(x_c - bw / 2)
        y_min = int(y_c - bh / 2)
        x_max = int(x_c + bw / 2)
        y_max = int(y_c + bh / 2)
      
        return np.array([x_min, y_min, x_max, y_max])

 
    parts = lines[line_to_segment].strip().split()
    if len(parts) != 5:
        raise ValueError(f"Invalid line format at line {line_to_segment}: {parts}")

    cls_id, x_c, y_c, bw, bh = map(float, parts)
    cls_id = int(cls_id)

 

    box = yolo_to_xyxy([x_c, y_c, bw, bh], w, h)
    masks, scores, _ = predictor.predict(
        box=box,
        multimask_output=True
    )

    best_mask = masks[np.argmax(scores)]

    mask_filename = f"{os.path.splitext(os.path.basename(image_path))[0]}_mask_line{line_to_segment}.png"
    mask_path = os.path.join(folder, mask_filename)
    cv2.imwrite(mask_path, best_mask.astype(np.uint8) * 255)

    
    return mask_path





def remove_background(image_path, mask_path, file_path, bg_color=(255, 255, 255)):
    image = cv2.imread(image_path)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    
    _, mask = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY)
    mask_3ch = cv2.merge([mask, mask, mask])
    object_only = cv2.bitwise_and(image, mask_3ch)
    bg = np.full_like(image, bg_color, dtype=np.uint8)
    result = np.where(mask_3ch == 0, bg, object_only)
    cv2.imwrite(file_path, result)

    return file_path








