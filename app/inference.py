import json
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision import models

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MODEL_PATH = "../models/model_1/model_1.pth"
CLASS_NAMES_PATH = "../models/model_1/class_names.json"


with open(CLASS_NAMES_PATH, "r") as f:
    class_names = json.load(f)

with open("../models/model_1/nutrition_db.json", "r") as f:
    nutrition_db = json.load(f)


NUM_CLASSES = len(class_names)


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


model = models.resnet18(weights=None)

in_features = model.fc.in_features

model.fc = nn.Linear(in_features, NUM_CLASSES)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model=model.to(DEVICE)
model.eval()


def predict_food(image_path):
    image=Image.open(image_path).convert("RGB")
    image_tensor=transform(image)
    image_tensor=image_tensor.unsqueeze(0)
    image_tensor=image_tensor.to(DEVICE)
    with torch.no_grad():
        logits=model(image_tensor)
        probs=torch.softmax(logits, dim=1)
        confidence, predicted_idx = torch.max(probs, dim=1)
    
    predicted_class=class_names[predicted_idx.item()]
    confidence=confidence.item()
    return predicted_class, confidence

def calculate_nutrition(dish_name, weight):

    nutrition=nutrition_db[dish_name]
    factor=weight / 100

    calories=nutrition["calories"] * factor
    protein=nutrition["protein"] * factor
    fat=nutrition["fat"] * factor
    carbs=nutrition["carbs"] * factor

    return {
        "calories": round(calories, 1),
        "protein": round(protein, 1),
        "fat": round(fat, 1),
        "carbs": round(carbs, 1)
    }